"""Constants for the Creality 3D Printer integration."""

from __future__ import annotations

import logging
from enum import IntEnum
from typing import Final

DOMAIN: Final = "creality_3dprinter"

LOGGER: Final = logging.getLogger(__package__)

DEFAULT_PORT: Final = 9999

UPDATE_INTERVAL_NORMAL: Final = 30
UPDATE_INTERVAL_PRINTING: Final = 5


class PrinterState(IntEnum):
    """States reported by the printer."""

    UNKNOWN = 0
    PRINTING = 1
    COMPLETE = 2
    IDLE = 4
    PAUSED = 5


# Single source of truth for the state sensor options and translations.
STATE_NAMES: Final[dict[int, str]] = {
    state.value: state.name.lower() for state in PrinterState
}
