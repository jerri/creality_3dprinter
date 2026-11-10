"""Test the Creality 3D Printer integration setup."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.creality_3dprinter.api import CrealityPrinterError
from custom_components.creality_3dprinter.const import DOMAIN

PATCH_GET_STATUS = (
    "custom_components.creality_3dprinter.api.CrealityPrinter.get_status"
)
STATE_ENTITY_ID = "sensor.creality_printer_state"


def _create_entry() -> MockConfigEntry:
    """Return a mock config entry for the printer."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="creality",
        unique_id="creality",
        data={CONF_HOST: "1.1.1.1", CONF_PORT: 9999},
    )


async def test_setup_and_unload_entry(
    hass: HomeAssistant, printer_status: dict[str, Any]
) -> None:
    """Test setting up and unloading the integration."""
    entry = _create_entry()
    entry.add_to_hass(hass)

    with patch(PATCH_GET_STATUS, return_value=printer_status):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    state = hass.states.get(STATE_ENTITY_ID)
    assert state is not None
    assert state.state == "idle"

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_offline_creates_unavailable_entities(
    hass: HomeAssistant,
) -> None:
    """Test that setup succeeds with unavailable entities when the printer is off."""
    entry = _create_entry()
    entry.add_to_hass(hass)

    with patch(PATCH_GET_STATUS, side_effect=CrealityPrinterError("offline")):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    state = hass.states.get(STATE_ENTITY_ID)
    assert state is not None
    assert state.state == STATE_UNAVAILABLE

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


async def test_entities_recover_when_printer_comes_online(
    hass: HomeAssistant, printer_status: dict[str, Any]
) -> None:
    """Test that entities become available after a successful refresh."""
    entry = _create_entry()
    entry.add_to_hass(hass)

    with patch(PATCH_GET_STATUS, side_effect=CrealityPrinterError("offline")):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get(STATE_ENTITY_ID)
    assert state is not None
    assert state.state == STATE_UNAVAILABLE

    coordinator = entry.runtime_data
    with patch(PATCH_GET_STATUS, return_value=printer_status):
        await coordinator.async_refresh()
        await hass.async_block_till_done()

    state = hass.states.get(STATE_ENTITY_ID)
    assert state is not None
    assert state.state == "idle"

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


async def test_entities_become_unavailable_when_printer_goes_offline(
    hass: HomeAssistant, printer_status: dict[str, Any]
) -> None:
    """Test that a failed refresh marks the entities unavailable."""
    entry = _create_entry()
    entry.add_to_hass(hass)

    with patch(PATCH_GET_STATUS, return_value=printer_status):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get(STATE_ENTITY_ID)
    assert state is not None
    assert state.state == "idle"

    with patch(PATCH_GET_STATUS, side_effect=CrealityPrinterError("offline")):
        await entry.runtime_data.async_refresh()
        await hass.async_block_till_done()

    state = hass.states.get(STATE_ENTITY_ID)
    assert state is not None
    assert state.state == STATE_UNAVAILABLE

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
