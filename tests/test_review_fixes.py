from pathlib import Path

import pytest

from modules.forecast import build_linear_forecast
from modules.i18n import translate


def test_constant_series_reliability_is_unavailable():
    result = build_linear_forecast([
        {"month": "2024-01", "revenue": 100.0},
        {"month": "2024-02", "revenue": 100.0},
    ])
    assert result["model"]["r_squared_interpretable"] is False
    assert result["model"]["reliability"] == "unavailable"


def test_weak_forecast_is_labelled_low():
    result = build_linear_forecast([
        {"month": "2024-01", "revenue": 100.0},
        {"month": "2024-02", "revenue": 400.0},
        {"month": "2024-03", "revenue": 50.0},
        {"month": "2024-04", "revenue": 300.0},
    ])
    assert result["model"]["reliability"] in {"low", "moderate", "high"}


def test_translation_formatting_errors_are_not_silent():
    with pytest.raises(ValueError):
        translate("revenue.growth.detail", "en")
