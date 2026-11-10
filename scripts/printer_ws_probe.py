#!/usr/bin/env python3
"""Continuously monitor the Creality printer websocket.

This is a development helper, not part of the Home Assistant integration.
It connects to the printer's websocket on port 9999, keeps the connection
open, and prints every frame it receives. Frames and connection events can
optionally be written to a JSON Lines file for later analysis.

The tool is read-only: it never sends commands to the printer. While it
holds the connection open, the printer's web UI may be unable to connect if
the printer only allows one websocket client.

Examples:
    python scripts/printer_ws_probe.py 192.168.1.50
    python scripts/printer_ws_probe.py 192.168.1.50 --output frames.jsonl
    python scripts/printer_ws_probe.py 192.168.1.50 --duration 120
    python scripts/printer_ws_probe.py 192.168.1.50 --no-reconnect
    python scripts/printer_ws_probe.py 192.168.1.50 --ping-interval 0
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TextIO

import websockets
from websockets.exceptions import WebSocketException

DEFAULT_PORT = 9999
DEFAULT_OPEN_TIMEOUT = 5.0
DEFAULT_PING_INTERVAL = 20.0
DEFAULT_PING_TIMEOUT = 20.0
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_MAX_RETRY_DELAY = 30.0


def _timestamp() -> str:
    """Return an ISO 8601 UTC timestamp with millisecond precision."""
    return datetime.now(UTC).isoformat(timespec="milliseconds")


class FrameWriter:
    """Print frames and optionally write them as JSON Lines."""

    def __init__(self, output: Path | None, append: bool) -> None:
        """Initialize the writer."""
        self._output = output
        self._file: TextIO | None = None
        self._frames = 0
        self._started = time.monotonic()

        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            mode = "a" if append else "w"
            self._file = output.open(mode, encoding="utf-8")

    @property
    def frames(self) -> int:
        """Return the number of received frames."""
        return self._frames

    def _record(self, record: dict[str, Any]) -> str:
        """Write a record to the JSON Lines file and return its timestamp."""
        timestamp = _timestamp()
        record = {"timestamp": timestamp, **record}

        if self._file is not None:
            self._file.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._file.flush()

        return timestamp

    def event(self, event: str, **details: Any) -> None:
        """Print and record a connection event."""
        timestamp = self._record({"event": event, **details})
        detail_text = " ".join(f"{key}={value}" for key, value in details.items())
        print(f"{timestamp} EVENT {event} {detail_text}".rstrip(), flush=True)

    def frame(self, raw: str | bytes) -> None:
        """Print and record a received websocket frame."""
        if isinstance(raw, bytes):
            text = raw.decode("utf-8", errors="replace")
        else:
            text = raw

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None

        self._frames += 1
        if data is None:
            timestamp = self._record(
                {"event": "frame", "direction": "rx", "raw": text}
            )
            print(f"{timestamp} RX {text}", flush=True)
        else:
            timestamp = self._record(
                {"event": "frame", "direction": "rx", "data": data}
            )
            compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            print(f"{timestamp} RX {compact}", flush=True)

    def close(self) -> None:
        """Close the output file."""
        if self._file is not None:
            self._file.close()

    def summary(self) -> None:
        """Print a short summary of the probe session."""
        elapsed = time.monotonic() - self._started
        print(
            f"Received {self._frames} frame(s) in {elapsed:.1f} second(s).",
            flush=True,
        )
        if self._output is not None:
            print(f"JSON Lines log written to {self._output}.", flush=True)


async def _probe(args: argparse.Namespace, writer: FrameWriter) -> None:
    """Keep a websocket connection open and log every frame."""
    url = f"ws://{args.host}:{args.port}/"
    retry_delay = args.retry_delay
    attempt = 1

    while True:
        writer.event("connecting", url=url, attempt=attempt)
        try:
            async with websockets.connect(
                url,
                open_timeout=args.open_timeout,
                close_timeout=1,
                ping_interval=args.ping_interval,
                ping_timeout=args.ping_timeout,
            ) as websocket:
                writer.event(
                    "connected",
                    url=url,
                    subprotocol=websocket.subprotocol,
                )
                retry_delay = args.retry_delay
                attempt = 1

                async for message in websocket:
                    writer.frame(message)

                writer.event(
                    "closed",
                    code=websocket.close_code,
                    reason=websocket.close_reason,
                )
        except asyncio.CancelledError:
            raise
        except (OSError, WebSocketException) as err:
            writer.event("error", error=f"{type(err).__name__}: {err}")

        if not args.reconnect:
            break

        writer.event("reconnecting", delay=retry_delay)
        await asyncio.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, args.max_retry_delay)
        attempt += 1


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Continuously read frames from a Creality printer websocket. "
            "The tool is read-only and never sends commands."
        )
    )
    parser.add_argument("host", help="Printer hostname or IP address.")
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Websocket port (default: {DEFAULT_PORT}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write frames and connection events to this JSON Lines file.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to the output file instead of overwriting it.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0,
        help="Stop after this many seconds (default: run until interrupted).",
    )
    parser.add_argument(
        "--no-reconnect",
        action="store_false",
        dest="reconnect",
        help="Exit when the connection closes instead of reconnecting.",
    )
    parser.add_argument(
        "--open-timeout",
        type=float,
        default=DEFAULT_OPEN_TIMEOUT,
        help=f"Connection timeout in seconds (default: {DEFAULT_OPEN_TIMEOUT}).",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=DEFAULT_RETRY_DELAY,
        help=(
            "Initial reconnect delay in seconds "
            f"(default: {DEFAULT_RETRY_DELAY})."
        ),
    )
    parser.add_argument(
        "--max-retry-delay",
        type=float,
        default=DEFAULT_MAX_RETRY_DELAY,
        help=(
            "Maximum reconnect delay in seconds "
            f"(default: {DEFAULT_MAX_RETRY_DELAY})."
        ),
    )
    parser.add_argument(
        "--ping-interval",
        type=float,
        default=DEFAULT_PING_INTERVAL,
        help=(
            "Websocket ping interval in seconds; set to 0 to disable "
            f"(default: {DEFAULT_PING_INTERVAL})."
        ),
    )
    parser.add_argument(
        "--ping-timeout",
        type=float,
        default=DEFAULT_PING_TIMEOUT,
        help=(
            "Websocket ping timeout in seconds "
            f"(default: {DEFAULT_PING_TIMEOUT})."
        ),
    )

    args = parser.parse_args(argv)
    if args.duration < 0:
        parser.error("--duration must be zero or greater")
    if args.open_timeout <= 0:
        parser.error("--open-timeout must be greater than zero")
    if args.retry_delay <= 0:
        parser.error("--retry-delay must be greater than zero")
    if args.max_retry_delay < args.retry_delay:
        parser.error(
            "--max-retry-delay must be greater than or equal to --retry-delay"
        )
    if args.ping_interval <= 0:
        args.ping_interval = None
        args.ping_timeout = None
    elif args.ping_timeout <= 0:
        args.ping_timeout = None
    return args


def main(argv: list[str] | None = None) -> int:
    """Run the websocket probe."""
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    writer = FrameWriter(args.output, args.append)

    try:
        with suppress(KeyboardInterrupt, TimeoutError):
            if args.duration > 0:

                async def _run_with_timeout() -> None:
                    async with asyncio.timeout(args.duration):
                        await _probe(args, writer)

                asyncio.run(_run_with_timeout())
            else:
                asyncio.run(_probe(args, writer))
    finally:
        writer.summary()
        writer.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
