"""The Creality 3D Printer integration."""

from __future__ import annotations

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .api import CrealityPrinter
from .coordinator import Creality3DPrinterConfigEntry, Creality3DPrinterCoordinator

_PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: Creality3DPrinterConfigEntry
) -> bool:
    """Set up Creality 3D Printer from a config entry."""
    client = CrealityPrinter(entry.data[CONF_HOST], entry.data[CONF_PORT])
    coordinator = Creality3DPrinterCoordinator(hass, entry, client)

    # The printer is usually powered off. A failed first refresh must not
    # prevent the entry from loading; entities become available automatically
    # once the printer is reachable again.
    await coordinator.async_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: Creality3DPrinterConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
