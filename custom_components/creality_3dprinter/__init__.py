"""The Creality 3d Printer integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import CrealityPrinter
from .coordinator import Creality3DPrinterCoordinator, Creality3DPrinterConfigEntry

_PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: Creality3DPrinterConfigEntry) -> bool:
    """Set up Creality 3d Printer from a config entry."""

    api = CrealityPrinter(entry.data['host'], entry.data['port'])

    coordinator = Creality3DPrinterCoordinator(hass, entry, api)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: Creality3DPrinterConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
