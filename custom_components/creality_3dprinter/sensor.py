"""Support for Creality 3D Printer sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .const import STATE_NAMES, PrinterState
from .coordinator import Creality3DPrinterConfigEntry, Creality3DPrinterCoordinator
from .entity import Creality3DPrinterEntity

PARALLEL_UPDATES = 0


def _state_name(status: dict[str, Any]) -> str:
    """Return the state name for a printer status."""
    return STATE_NAMES.get(status.get("state"), STATE_NAMES[PrinterState.UNKNOWN])


def _print_end_time(status: dict[str, Any]) -> datetime | None:
    """Return the estimated print end time, if a print is running."""
    if status.get("state") != PrinterState.PRINTING:
        return None

    remaining = status.get("printLeftTime")
    if not isinstance(remaining, (int, float)) or remaining <= 0:
        return None

    return dt_util.utcnow() + timedelta(seconds=remaining)


@dataclass(frozen=True, kw_only=True)
class Creality3DPrinterSensorEntityDescription(SensorEntityDescription):
    """Describes a Creality 3D Printer sensor entity."""

    value_fn: Callable[[dict[str, Any]], StateType | datetime]
    """Function to extract the sensor value from the printer status."""


SENSORS: tuple[Creality3DPrinterSensorEntityDescription, ...] = (
    Creality3DPrinterSensorEntityDescription(
        key="state",
        translation_key="state",
        device_class=SensorDeviceClass.ENUM,
        options=[state.name.lower() for state in PrinterState],
        value_fn=_state_name,
    ),
    Creality3DPrinterSensorEntityDescription(
        key="nozzleTemp",
        translation_key="nozzleTemp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status.get("nozzleTemp"),
    ),
    Creality3DPrinterSensorEntityDescription(
        key="targetNozzleTemp",
        translation_key="targetNozzleTemp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status.get("targetNozzleTemp"),
    ),
    Creality3DPrinterSensorEntityDescription(
        key="bedTemp0",
        translation_key="bedTemp0",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status.get("bedTemp0"),
    ),
    Creality3DPrinterSensorEntityDescription(
        key="targetBedTemp0",
        translation_key="targetBedTemp0",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status.get("targetBedTemp0"),
    ),
    Creality3DPrinterSensorEntityDescription(
        key="printProgress",
        translation_key="printProgress",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status.get("printProgress"),
    ),
    Creality3DPrinterSensorEntityDescription(
        key="TotalLayer",
        translation_key="TotalLayer",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status.get("TotalLayer"),
    ),
    Creality3DPrinterSensorEntityDescription(
        key="layer",
        translation_key="layer",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status.get("layer"),
    ),
    Creality3DPrinterSensorEntityDescription(
        key="printFileName",
        translation_key="printFileName",
        value_fn=lambda status: status.get("printFileName") or None,
    ),
    Creality3DPrinterSensorEntityDescription(
        key="printLeftTime",
        translation_key="printLeftTime",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_print_end_time,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: Creality3DPrinterConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data
    entities = [
        Creality3DPrinterSensor(coordinator, description)
        for description in SENSORS
    ]
    async_add_entities(entities)


class Creality3DPrinterSensor(Creality3DPrinterEntity, SensorEntity):
    """Representation of a Creality 3D Printer sensor."""

    entity_description: Creality3DPrinterSensorEntityDescription

    def __init__(
        self,
        coordinator: Creality3DPrinterCoordinator,
        description: Creality3DPrinterSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}-{description.key}"

    @property
    def native_value(self) -> StateType | datetime:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
