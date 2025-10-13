import websockets
import json

OPEN_TIMEOUT = 3


class CrealityPrinter:
    """Interact with the Creality 3D printer websocket API."""

    def __init__(self, host: str, port: int = 9999):
        self._host = host
        self._port = port

    async def get_status(self) -> dict:
        """Get the current status from the printer into a JSON."""
        uri = f"ws://{self._host}:{self._port}/"
        try:
            async with websockets.connect(uri, open_timeout=OPEN_TIMEOUT) as ws:
                response = await ws.recv()
                return json.loads(response)
        except TimeoutError:
            return {"error": "Timeout connecting to server"}
        except OSError:
            return {"error": "Error connecting to server. Maybe printer is turned off?"}
