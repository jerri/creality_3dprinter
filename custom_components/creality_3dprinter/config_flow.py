"""Config flow for the Creality 3D Printer integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import HomeAssistantError

from .api import CrealityPrinter, CrealityPrinterError
from .const import DEFAULT_PORT, DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): vol.All(str, vol.Length(min=1)),
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
    }
)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


async def _validate_input(data: dict[str, Any]) -> dict[str, str]:
    """Validate the input and return the config entry title and unique ID."""
    client = CrealityPrinter(data[CONF_HOST], data[CONF_PORT])

    try:
        status = await client.get_status()
    except CrealityPrinterError as err:
        raise CannotConnect from err

    # Fall back to the configured host if the printer does not report a name.
    hostname = str(status.get("hostname") or data[CONF_HOST])
    return {"title": hostname, "unique_id": hostname}


class Creality3DPrinterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Creality 3D Printer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await _validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
