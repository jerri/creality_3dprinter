"""Base entity for the Creality 3D Printer integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Creality3DPrinterCoordinator


class Creality3DPrinterEntity(CoordinatorEntity[Creality3DPrinterCoordinator]):
    """Base class for Creality 3D Printer entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: Creality3DPrinterCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        data = coordinator.data or {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            manufacturer="Creality",
            model=data.get("modelVersion"),
            configuration_url=f"http://{coordinator.client.host}",
        )
