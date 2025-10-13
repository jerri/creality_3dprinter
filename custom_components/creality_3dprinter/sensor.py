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

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import Creality3DPrinterConfigEntry
from .coordinator import Creality3DPrinterCoordinator
from .entity import Creality3DPrinterEntity

PARALLEL_UPDATES = 0
STATES = {0: 'unknown', 1: 'printing', 2: 'complete', 4: 'idle', 5: 'paused', 99: 'offline'}
STATE_VALUES = list(STATES.values())


@dataclass(frozen=True, kw_only=True)
class Creality3DPrinterSensorEntityDescription(SensorEntityDescription):
    """Describes Creality 3D Printer sensor entity."""

    value_fn: Callable[[dict], StateType]
    """Function to extract the sensor value from the API data."""


SENSORS: tuple[Creality3DPrinterSensorEntityDescription, ...] = (
    Creality3DPrinterSensorEntityDescription(
        key="state",
        name="Printer State",
        device_class=SensorDeviceClass.ENUM,
        options=STATE_VALUES,
        value_fn=lambda status: STATES[status['state']] if status['state'] in STATES else 'unknown',
    ),
    Creality3DPrinterSensorEntityDescription(
        key="nozzleTemp",
        name="Nozzle Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['nozzleTemp'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="targetNozzleTemp",
        name="Target Nozzle Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['targetNozzleTemp'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="bedTemp0",
        name="Bed Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['bedTemp0'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="targetBedTemp0",
        name="Target Bed Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['targetBedTemp0'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="printProgress",
        name="Print Progress",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['printProgress'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="TotalLayer",
        name="Total Layers",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['TotalLayer'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="layer",
        name="Current Layer",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status['layer'],
    ),
    Creality3DPrinterSensorEntityDescription(
        key="printFileName",
        name="Print File Name",
        value_fn=lambda status: status['printFileName'],
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: Creality3DPrinterConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    listener: Callable[[], None] | None = None
    not_setup: set[Creality3DPrinterSensorEntityDescription] = set(SENSORS)

    @callback
    def add_entities() -> None:
        nonlocal not_setup, listener
        sensor_descriptions = not_setup
        not_setup = set()
        sensors = []
        for description in sensor_descriptions:
            if description.value_fn(coordinator.data.data) is None:
                not_setup.add(description)
            else:
                sensors.append(Creality3DPrinterSensor(coordinator, description))

        if sensors:
            async_add_entities(sensors)
        if not_setup:
            if not listener:
                listener = coordinator.async_add_listener(add_entities)
        elif listener:
            listener()

    add_entities()


class Creality3DPrinterSensor(Creality3DPrinterEntity, SensorEntity):

    def __init__(self, coordinator: Creality3DPrinterCoordinator, description: Creality3DPrinterSensorEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.serial_number}-{description.key}"

    @property
    def native_value(self) -> StateType:
        return self.entity_description.value_fn(self.coordinator.data.data)
