import inspect
from pathlib import Path

from openpyxl import Workbook

from modules.excel_exporter import _create_forecast_sheet
from modules.kpi_engine import load_data, validate_data
from modules.visualizer import CHART_DIR, PROJECT_ROOT


def test_validator_and_loader_are_keyword_only():
    load_signature = inspect.signature(load_data)
    validate_signature = inspect.signature(validate_data)

    assert all(
        parameter.kind
        is inspect.Parameter.KEYWORD_ONLY
        for parameter in load_signature.parameters.values()
    )
    assert all(
        parameter.kind
        is inspect.Parameter.KEYWORD_ONLY
        for parameter in validate_signature.parameters.values()
    )


def test_chart_directory_is_project_relative():
    assert CHART_DIR.is_absolute()
    assert CHART_DIR == (
        PROJECT_ROOT
        / "reports"
        / "charts"
    )


def test_forecast_sheet_filter_covers_data_rows():
    workbook = Workbook()
    workbook.remove(workbook.active)

    forecast = {
        "historical": [
            {
                "month": "2024-01",
                "revenue": 100.0,
                "trend_value": 110.0,
            },
            {
                "month": "2024-02",
                "revenue": 120.0,
                "trend_value": 120.0,
            },
        ],
        "forecast": [
            {
                "month": "2024-03",
                "forecast_revenue": 130.0,
            }
        ],
        "model": {
            "name": "Linear Regression",
            "method": "NumPy polyfit",
            "slope": 10.0,
            "r_squared": 0.8,
            "r_squared_interpretable": True,
            "reliability": "high",
            "direction": "Growing",
        },
        "assumptions": [
            "Directional estimate only.",
        ],
    }

    _create_forecast_sheet(
        workbook,
        forecast,
    )

    worksheet = workbook[
        "Revenue Forecast"
    ]

    assert worksheet.auto_filter.ref == "A3:D6"

    for row in worksheet.iter_rows(
        min_row=4,
        max_row=6,
        min_col=1,
        max_col=4,
    ):
        assert all(
            cell.border.left.style is not None
            for cell in row
        )


def test_final_console_labels_are_semantically_explicit():
    project_root = Path(__file__).resolve().parent.parent
    main_source = (
        project_root
        / "main.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "Highest Revenue per Active Customer Segment"
        in main_source
    )
    assert 'f"{mom_growth:+.2f}%"' in main_source
