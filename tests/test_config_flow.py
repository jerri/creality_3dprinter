"""Test the Creality 3D Printer config flow."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.creality_3dprinter.api import CrealityPrinterError
from custom_components.creality_3dprinter.const import DOMAIN

PATCH_GET_STATUS = (
    "custom_components.creality_3dprinter.config_flow.CrealityPrinter.get_status"
)
USER_INPUT = {CONF_HOST: "1.1.1.1", CONF_PORT: 9999}


async def _start_flow(hass: HomeAssistant) -> dict[str, Any]:
    """Start a user config flow and return the initial form result."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}
    return result


async def test_form(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    printer_status: dict[str, Any],
) -> None:
    """Test creating a config entry."""
    result = await _start_flow(hass)

    with patch(PATCH_GET_STATUS, return_value=printer_status):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "creality"
    assert result["data"] == USER_INPUT

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    assert entries[0].unique_id == "creality"
    mock_setup_entry.assert_called_once()


async def test_form_cannot_connect(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    printer_status: dict[str, Any],
) -> None:
    """Test handling a connection error and recovering."""
    result = await _start_flow(hass)

    with patch(PATCH_GET_STATUS, side_effect=CrealityPrinterError("offline")):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    with patch(PATCH_GET_STATUS, return_value=printer_status):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "creality"
    mock_setup_entry.assert_called_once()


async def test_form_already_configured(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    printer_status: dict[str, Any],
) -> None:
    """Test that the same printer cannot be added twice."""
    result = await _start_flow(hass)
    with patch(PATCH_GET_STATUS, return_value=printer_status):
        first_result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
        await hass.async_block_till_done()

    assert first_result["type"] is FlowResultType.CREATE_ENTRY

    result = await _start_flow(hass)
    with patch(PATCH_GET_STATUS, return_value=printer_status):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    mock_setup_entry.assert_called_once()


async def test_form_without_hostname(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    printer_status: dict[str, Any],
) -> None:
    """Test falling back to the host when no hostname is reported."""
    status = dict(printer_status)
    status.pop("hostname")

    result = await _start_flow(hass)
    with patch(PATCH_GET_STATUS, return_value=status):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == USER_INPUT[CONF_HOST]

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    assert entries[0].unique_id == USER_INPUT[CONF_HOST]
    mock_setup_entry.assert_called_once()
