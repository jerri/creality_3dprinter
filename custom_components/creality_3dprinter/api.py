"""Client for the Creality 3D printer websocket API."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import websockets
from websockets.exceptions import WebSocketException

from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_PORT

OPEN_TIMEOUT = 3
RECEIVE_TIMEOUT = 5
CLOSE_TIMEOUT = 1


class CrealityPrinterError(HomeAssistantError):
    """Error while communicating with the printer."""


class CrealityPrinter:
    """Interact with the Creality 3D printer websocket API."""

    def __init__(self, host: str, port: int | str = DEFAULT_PORT) -> None:
        """Initialize the printer client."""
        self.host = host
        self.port = int(port)

    @property
    def websocket_url(self) -> str:
        """Return the websocket URL of the printer."""
        return f"ws://{self.host}:{self.port}/"

    async def get_status(self) -> dict[str, Any]:
        """Return the current status reported by the printer."""
        try:
            async with websockets.connect(
                self.websocket_url,
                open_timeout=OPEN_TIMEOUT,
                close_timeout=CLOSE_TIMEOUT,
                ping_interval=None,
            ) as websocket:
                async with asyncio.timeout(RECEIVE_TIMEOUT):
                    response = await websocket.recv()
        except (OSError, WebSocketException) as err:
            # Timeouts and refused connections are both OSError subclasses.
            raise CrealityPrinterError(
                f"Unable to connect to printer at {self.host}:{self.port}"
            ) from err

        try:
            data = json.loads(response)
        except (json.JSONDecodeError, UnicodeDecodeError) as err:
            raise CrealityPrinterError("Printer returned invalid data") from err

        if not isinstance(data, dict):
            raise CrealityPrinterError("Printer returned an unexpected payload")

        return data
