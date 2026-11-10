"""Config flow for the Creality 3d Printer integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .api import CrealityPrinter, CrealityPrinterError

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default="9999"): str,
    }
)


class CrealityPrinterHub:

    def __init__(self, data) -> None:
        """Initialize."""
        self.host = data[CONF_HOST]
        self.port = data[CONF_PORT]
        self.status: dict | Any = None

    async def getdata(self) -> bool:
        api = CrealityPrinter(self.host, self.port)
        try:
            self.status = await api.get_status()
        except CrealityPrinterError:
            return False
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    hub = CrealityPrinterHub(data)

    if not await hub.getdata():
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {"title": hub.status['hostname']}


class Creality3DPrinterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Creality 3d Printer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    info['title'], raise_on_progress=False
                )
                if self.source == SOURCE_USER:
                    self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
