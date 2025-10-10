"""Object to manage fetching Creality Printer data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CrealityPrinter
from .const import DOMAIN, LOGGER

type Creality3DPrinterConfigEntry = ConfigEntry[Creality3DPrinterCoordinator]


@dataclass
class Creality3DPrinterData:

    data: dict


class Creality3DPrinterCoordinator(DataUpdateCoordinator[Creality3DPrinterData]):

    config_entry: Creality3DPrinterConfigEntry

    def __init__(self, hass: HomeAssistant, configEntry: Creality3DPrinterConfigEntry, client: CrealityPrinter) -> None:
        super().__init__(hass, logger=LOGGER, config_entry=configEntry, name=f"Creality 3d Printer {client._host}", update_interval=timedelta(minutes=1))
        self.client = client
        assert self.config_entry.unique_id
        self.serial_number = self.config_entry.unique_id

    async def _async_setup(self) -> None:
        """Don't think this is necessary."""
        pass

    async def _async_update_data(self) -> Creality3DPrinterData:
        data = await self.client.get_status()
        if "error" in data:
            raise UpdateFailed(translation_domain=DOMAIN, translation_key="update_error", translation_placeholders=data)
        return Creality3DPrinterData(data)
