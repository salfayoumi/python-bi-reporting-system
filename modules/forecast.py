"""
modules/forecast.py

Generates a short-term revenue forecast using linear regression
with NumPy polyfit.

The forecast is intended as a directional estimate only. It does
not account for seasonality, market shocks, campaigns, or other
external business factors.
"""

import numpy as np
import pandas as pd


DEFAULT_FORECAST_MONTHS = 3
STABLE_TREND_TOLERANCE = 0.01

REQUIRED_MONTHLY_COLUMNS = {
    "month",
    "revenue",
}

FORECAST_ASSUMPTIONS = [
    "The forecast is based only on historical monthly revenue.",
    "The model assumes a linear relationship over time.",
    "Seasonality and external business factors are not included.",
    "Forecast values are directional estimates, not guarantees.",
]


def prepare_monthly_revenue(
    monthly_revenue: list[dict],
) -> pd.DataFrame:
    """
    Convert monthly KPI records into a clean chronological DataFrame.

    Expected input:
        [
            {
                "month": "2024-01",
                "revenue": 100000.0,
            },
            ...
        ]

    Raises:
        ValueError:
            If required columns are missing, the dataset is empty,
            values are invalid, or fewer than two valid months exist.
    """

    dataframe = pd.DataFrame(
        monthly_revenue
    )

    missing_columns = (
        REQUIRED_MONTHLY_COLUMNS
        - set(dataframe.columns)
    )

    if missing_columns:
        missing_names = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            "Monthly revenue data is missing "
            f"required columns: {missing_names}"
        )

    if dataframe.empty:
        raise ValueError(
            "Monthly revenue data is empty."
        )

    dataframe = dataframe.copy()

    dataframe["month"] = pd.to_datetime(
        dataframe["month"],
        format="%Y-%m",
        errors="coerce",
    )

    dataframe["revenue"] = pd.to_numeric(
        dataframe["revenue"],
        errors="coerce",
    )

    invalid_month_count = int(
        dataframe["month"]
        .isna()
        .sum()
    )

    invalid_revenue_count = int(
        dataframe["revenue"]
        .isna()
        .sum()
    )

    if invalid_month_count:
        raise ValueError(
            f"{invalid_month_count} invalid "
            "month value(s) found."
        )

    if invalid_revenue_count:
        raise ValueError(
            f"{invalid_revenue_count} invalid "
            "revenue value(s) found."
        )

    dataframe = (
        dataframe
        .sort_values("month")
        .drop_duplicates(
            subset=["month"],
            keep="last",
        )
        .reset_index(
            drop=True
        )
    )

    if len(dataframe) < 2:
        raise ValueError(
            "At least two monthly revenue records "
            "are required to create a linear forecast."
        )

    return dataframe


def _calculate_r_squared(
    actual_values: np.ndarray,
    fitted_values: np.ndarray,
) -> float:
    """Calculate the coefficient of determination for the model."""

    residuals = (
        actual_values
        - fitted_values
    )

    residual_sum_of_squares = float(
        np.sum(
            residuals ** 2
        )
    )

    total_sum_of_squares = float(
        np.sum(
            (
                actual_values
                - actual_values.mean()
            )
            ** 2
        )
    )

    if total_sum_of_squares == 0:
        return 1.0

    return (
        1
        - residual_sum_of_squares
        / total_sum_of_squares
    )


def _determine_trend_direction(
    slope: float,
    average_monthly_revenue: float,
) -> str:
    """Classify the fitted revenue trend."""

    trend_tolerance = (
        average_monthly_revenue
        * STABLE_TREND_TOLERANCE
    )

    if slope > trend_tolerance:
        return "Growing"

    if slope < -trend_tolerance:
        return "Declining"

    return "Stable"


def _build_historical_records(
    historical_data: pd.DataFrame,
    fitted_values: np.ndarray,
) -> list[dict]:
    """Convert historical and fitted values into report records."""

    records = []

    for index, row in enumerate(
        historical_data.itertuples(
            index=False
        )
    ):
        records.append(
            {
                "month": row.month.strftime(
                    "%Y-%m"
                ),
                "revenue": round(
                    float(row.revenue),
                    2,
                ),
                "trend_value": round(
                    float(
                        fitted_values[index]
                    ),
                    2,
                ),
            }
        )

    return records


def _build_forecast_records(
    future_months: pd.DatetimeIndex,
    forecast_values: np.ndarray,
) -> list[dict]:
    """Convert future dates and predictions into report records."""

    return [
        {
            "month": month.strftime(
                "%Y-%m"
            ),
            "forecast_revenue": round(
                float(revenue),
                2,
            ),
        }
        for month, revenue in zip(
            future_months,
            forecast_values,
        )
    ]


def build_linear_forecast(
    monthly_revenue: list[dict],
    forecast_months: int = DEFAULT_FORECAST_MONTHS,
) -> dict:
    """
    Create a linear revenue forecast for future months.

    The model uses:

        revenue = slope × month_index + intercept

    Forecasted revenue values are limited to a minimum of zero.
    """

    if forecast_months < 1:
        raise ValueError(
            "forecast_months must be at least 1."
        )

    historical_data = prepare_monthly_revenue(
        monthly_revenue
    )

    historical_count = len(
        historical_data
    )

    historical_indexes = np.arange(
        historical_count,
        dtype=float,
    )

    historical_revenue = (
        historical_data["revenue"]
        .to_numpy(
            dtype=float
        )
    )

    slope, intercept = np.polyfit(
        historical_indexes,
        historical_revenue,
        1,
    )

    fitted_values = (
        slope
        * historical_indexes
        + intercept
    )

    r_squared = _calculate_r_squared(
        historical_revenue,
        fitted_values,
    )

    last_historical_month = (
        historical_data["month"]
        .iloc[-1]
    )

    future_month_dates = pd.date_range(
        start=(
            last_historical_month
            + pd.offsets.MonthBegin(1)
        ),
        periods=forecast_months,
        freq="MS",
    )

    future_indexes = np.arange(
        historical_count,
        historical_count
        + forecast_months,
        dtype=float,
    )

    future_revenue = (
        slope
        * future_indexes
        + intercept
    )

    future_revenue = np.maximum(
        future_revenue,
        0,
    )

    historical_records = (
        _build_historical_records(
            historical_data,
            fitted_values,
        )
    )

    forecast_records = (
        _build_forecast_records(
            future_month_dates,
            future_revenue,
        )
    )

    average_monthly_revenue = float(
        historical_revenue.mean()
    )

    trend_direction = (
        _determine_trend_direction(
            slope,
            average_monthly_revenue,
        )
    )

    return {
        "historical": historical_records,
        "forecast": forecast_records,
        "model": {
            "name": "Linear Regression",
            "method": "NumPy polyfit",
            "forecast_months": forecast_months,
            "slope": round(
                float(slope),
                2,
            ),
            "intercept": round(
                float(intercept),
                2,
            ),
            "r_squared": round(
                float(r_squared),
                4,
            ),
            "direction": trend_direction,
        },
        "assumptions": (
            FORECAST_ASSUMPTIONS.copy()
        ),
    }


def compute_revenue_forecast(
    kpis: dict,
    forecast_months: int = DEFAULT_FORECAST_MONTHS,
) -> dict:
    """Generate a forecast from KPI-engine monthly revenue records."""

    monthly_revenue = (
        kpis["trends"][
            "monthly_revenue"
        ]
    )

    return build_linear_forecast(
        monthly_revenue,
        forecast_months=forecast_months,
    )