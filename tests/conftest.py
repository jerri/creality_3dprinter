"""Common fixtures for the Creality 3D Printer tests."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Enable custom integrations in all tests."""
    yield


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.creality_3dprinter.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def printer_status() -> dict[str, Any]:
    """Return a sample printer status payload."""
    return {
        "hostname": "creality",
        "modelVersion": "Ender-3 V3 KE",
        "state": 4,
        "nozzleTemp": 24.5,
        "targetNozzleTemp": 0,
        "bedTemp0": 23.1,
        "targetBedTemp0": 0,
        "printProgress": 0,
        "TotalLayer": 0,
        "layer": 0,
        "printFileName": "",
        "printLeftTime": 0,
    }
