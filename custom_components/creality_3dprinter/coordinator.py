"""Object to manage fetching Creality Printer data."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CrealityPrinter, CrealityPrinterError
from .const import (
    LOGGER,
    UPDATE_INTERVAL_NORMAL,
    UPDATE_INTERVAL_PRINTING,
    PrinterState,
)

type Creality3DPrinterConfigEntry = ConfigEntry[Creality3DPrinterCoordinator]


class Creality3DPrinterCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch data from the printer and poll faster while it is printing."""

    config_entry: Creality3DPrinterConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: Creality3DPrinterConfigEntry,
        client: CrealityPrinter,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=f"Creality 3D Printer {client.host}",
            update_interval=timedelta(seconds=UPDATE_INTERVAL_NORMAL),
        )
        self.client = client
        self.device_id = config_entry.unique_id or config_entry.entry_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest status from the printer."""
        try:
            data = await self.client.get_status()
        except CrealityPrinterError as err:
            # Do not keep polling every 5 seconds while the printer is off.
            self.update_interval = timedelta(seconds=UPDATE_INTERVAL_NORMAL)
            raise UpdateFailed(f"Unable to fetch printer data: {err}") from err

        if data.get("state") == PrinterState.PRINTING:
            self.update_interval = timedelta(seconds=UPDATE_INTERVAL_PRINTING)
        else:
            self.update_interval = timedelta(seconds=UPDATE_INTERVAL_NORMAL)

        return data
