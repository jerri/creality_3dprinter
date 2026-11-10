"""Test the Creality 3D Printer sensor value helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from custom_components.creality_3dprinter.sensor import _print_end_time, _state_name


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations() -> None:
    """Skip the Home Assistant fixture for these pure unit tests."""


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ({"state": 0}, "unknown"),
        ({"state": 1}, "printing"),
        ({"state": 2}, "complete"),
        ({"state": 4}, "idle"),
        ({"state": 5}, "paused"),
        ({"state": 99}, "unknown"),
        ({}, "unknown"),
    ],
)
def test_state_name(status: dict[str, Any], expected: str) -> None:
    """Test mapping printer states to sensor states."""
    assert _state_name(status) == expected


@pytest.mark.parametrize(
    ("status", "expected_end_time"),
    [
        ({"state": 1, "printLeftTime": 60}, True),
        ({"state": 1, "printLeftTime": None}, False),
        ({"state": 1, "printLeftTime": 0}, False),
        ({"state": 1}, False),
        ({"state": 4, "printLeftTime": 60}, False),
    ],
)
def test_print_end_time(status: dict[str, Any], expected_end_time: bool) -> None:
    """Test the print end time guard against missing or invalid values."""
    result = _print_end_time(status)
    if expected_end_time:
        assert isinstance(result, datetime)
    else:
        assert result is None
