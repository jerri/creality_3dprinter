"""Base class for Creality3DPrinter entities."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import Creality3DPrinterCoordinator


class Creality3DPrinterEntity(CoordinatorEntity[Creality3DPrinterCoordinator]):

    _attr_has_entity_name = True

    def __init__(self, coordinator: Creality3DPrinterCoordinator) -> None:
        super().__init__(coordinator)
        data = coordinator.data.data
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.serial_number)},
            manufacturer="Creality",
            model=data['modelVersion'],
            model_id=data['modelVersion'],
            serial_number=coordinator.serial_number,
            sw_version=data['modelVersion'],
            connections={(dr.CONNECTION_NETWORK_MAC, coordinator.serial_number)}
        )
