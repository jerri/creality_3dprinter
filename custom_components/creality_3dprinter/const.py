"""Constants for the Creality 3d Printer integration."""

import logging

DOMAIN = "creality_3dprinter"

LOGGER = logging.getLogger(__package__)

UPDATE_INTERVAL_NORMAL = 30
UPDATE_INTERVAL_PRINTING = 5

OFFLINE_STATUS = {
    "modelVersion": "unavailable",
    "state": 99,
    "nozzleTemp": 0,
    "targetNozzleTemp": 0,
    "bedTemp0": 0,
    "targetBedTemp0": 0,
    "printProgress": 0,
    "TotalLayer": 0,
    "layer": 0,
    "printFileName": "",
    "printLeftTime": None,
}
