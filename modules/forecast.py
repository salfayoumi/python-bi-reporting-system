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

from modules.domain import (
    KPIBundle,
    ForecastReliability,
    FORECAST_LOW_R2_THRESHOLD,
    FORECAST_MODERATE_R2_THRESHOLD,
    classify_trend,
)


DEFAULT_FORECAST_MONTHS = 3

REQUIRED_MONTHLY_COLUMNS = {
    "month",
    "revenue",
}

FORECAST_ASSUMPTIONS = [
    "The forecast is based only on historical monthly revenue.",
    "Missing calendar months are retained with zero revenue.",
    "The model assumes a linear relationship over time.",
    "Seasonality and external business factors are not included.",
    "Forecast values are directional estimates, not guarantees.",
]


def prepare_monthly_revenue(
    monthly_revenue: list[dict],
) -> pd.DataFrame:
    """
    Convert monthly KPI records into a complete chronological DataFrame.

    Missing calendar months between the first and last observation are
    added with zero revenue so the time axis remains accurate.
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

    dataframe["month_period"] = (
        dataframe["month"]
        .dt.to_period("M")
    )

    monthly_series = (
        dataframe.groupby("month_period")[
            "revenue"
        ]
        .sum()
        .sort_index()
    )

    complete_periods = pd.period_range(
        start=monthly_series.index.min(),
        end=monthly_series.index.max(),
        freq="M",
    )

    monthly_series = monthly_series.reindex(
        complete_periods,
        fill_value=0.0,
    )

    dataframe = pd.DataFrame(
        {
            "month": (
                monthly_series.index
                .to_timestamp()
            ),
            "revenue": (
                monthly_series
                .to_numpy(dtype=float)
            ),
        }
    )

    if len(dataframe) < 2:
        raise ValueError(
            "At least two calendar months are required "
            "to create a linear forecast."
        )

    return dataframe


def _month_offsets(
    months: pd.Series | pd.DatetimeIndex,
    origin: pd.Timestamp,
) -> np.ndarray:
    """Return real calendar-month offsets from an origin month."""

    periods = pd.DatetimeIndex(
        months
    ).to_period("M")

    origin_period = origin.to_period("M")

    return np.array(
        [
            (
                period.year
                - origin_period.year
            )
            * 12
            + (
                period.month
                - origin_period.month
            )
            for period in periods
        ],
        dtype=float,
    )


def _calculate_r_squared(
    actual_values: np.ndarray,
    fitted_values: np.ndarray,
) -> tuple[float, bool]:
    """
    Calculate R-squared and whether it is statistically interpretable.

    A constant target series has no variance, so R-squared is undefined.
    It is represented as 0.0 for backward-compatible display together
    with an explicit interpretability flag.
    """

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

    if np.isclose(
        total_sum_of_squares,
        0.0,
    ):
        return 0.0, False

    return (
        1
        - residual_sum_of_squares
        / total_sum_of_squares,
        True,
    )



def _forecast_reliability(r_squared: float, interpretable: bool) -> str:
    """Classify forecast explanatory power for business-facing output."""

    if not interpretable:
        return ForecastReliability.UNAVAILABLE.value
    if r_squared < FORECAST_LOW_R2_THRESHOLD:
        return ForecastReliability.LOW.value
    if r_squared < FORECAST_MODERATE_R2_THRESHOLD:
        return ForecastReliability.MODERATE.value
    return ForecastReliability.HIGH.value


def _determine_trend_direction(
    slope: float,
    average_monthly_revenue: float,
) -> str:
    """Return the display label for the shared trend classification."""

    return classify_trend(
        slope,
        average_monthly_revenue,
    ).value.title()


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
    """Create a calendar-aware linear revenue forecast."""

    if forecast_months < 1:
        raise ValueError(
            "forecast_months must be at least 1."
        )

    historical_data = prepare_monthly_revenue(
        monthly_revenue
    )

    origin_month = (
        historical_data["month"]
        .iloc[0]
    )

    historical_indexes = _month_offsets(
        historical_data["month"],
        origin_month,
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

    (
        r_squared,
        r_squared_interpretable,
    ) = _calculate_r_squared(
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

    future_indexes = _month_offsets(
        future_month_dates,
        origin_month,
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
            "r_squared_interpretable": (
                r_squared_interpretable
            ),
            "reliability": _forecast_reliability(
                float(r_squared),
                r_squared_interpretable,
            ),
            "direction": trend_direction,
            "direction_code": trend_direction.casefold(),
        },
        "assumptions": (
            FORECAST_ASSUMPTIONS.copy()
        ),
    }


def compute_revenue_forecast(
    kpis: KPIBundle,
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
