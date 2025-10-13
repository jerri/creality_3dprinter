"""Support for Creality 3D Printer sensors."""

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util.dt import utcnow
from datetime import datetime, timedelta

from . import Creality3DPrinterConfigEntry
from .coordinator import Creality3DPrinterCoordinator
from .entity import Creality3DPrinterEntity

PARALLEL_UPDATES = 0
STATES = {0: 'unknown', 1: 'printing', 2: 'complete', 4: 'idle', 5: 'paused', 99: 'offline'}
STATE_VALUES = list(STATES.values())


@dataclass(frozen=True, kw_only=True)
class Creality3DPrinterSensorEntityDescription(SensorEntityDescription):
    """Describes Creality 3D Printer sensor entity."""

    value_fn: Callable[[dict], datetime | StateType]
    """Function to extract the sensor value from the API data."""


SENSORS: tuple[Creality3DPrinterSensorEntityDescription, ...] = (
    Creality3DPrinterSensorEntityDescription(
        key="state",
        translation_key="state",
        device_class=SensorDeviceClass.ENUM,
        options=STATE_VALUES,
        value_fn=lambda status: STATES[status['state']] if status['state'] in STATES else 'unknown',
    ),
    Creality3DPrinterSensorEntityDescription(
        key="nozzleTemp",
        translation_key="nozzleTemp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['nozzleTemp'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="targetNozzleTemp",
        translation_key="targetNozzleTemp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['targetNozzleTemp'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="bedTemp0",
        translation_key="bedTemp0",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['bedTemp0'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="targetBedTemp0",
        translation_key="targetBedTemp0",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['targetBedTemp0'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="printProgress",
        translation_key="printProgress",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['printProgress'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="TotalLayer",
        translation_key="TotalLayer",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['TotalLayer'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="layer",
        translation_key="layer",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['layer'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="printFileName",
        translation_key="printFileName",
        value_fn=lambda status: status['printFileName'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="printLeftTime",
        translation_key="printLeftTime",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda status: (utcnow() + timedelta(seconds=status['printLeftTime'])) if status['state'] == 1 and status['printLeftTime'] > 0 else None,
    )
)


async def async_setup_entry(hass: HomeAssistant, entry: Creality3DPrinterConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data

    sensors = []
    for description in SENSORS:
        sensors.append(Creality3DPrinterSensor(coordinator, description))

    async_add_entities(sensors)


class Creality3DPrinterSensor(Creality3DPrinterEntity, SensorEntity):

    def __init__(self, coordinator: Creality3DPrinterCoordinator, description: Creality3DPrinterSensorEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.serial_number}-{description.key}"

    @property
    def native_value(self) -> StateType:
        return self.entity_description.value_fn(self.coordinator.data.data)
