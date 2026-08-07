"""
Shared domain definitions for the BI reporting system.

Business rules and machine-readable states live here so calculations,
decision support, reporting, and dashboards use one source of truth.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, TypedDict


class TrendDirection(str, Enum):
    """Machine-readable long-term revenue trend states."""

    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"


class MomGrowthStatus(str, Enum):
    """Machine-readable month-over-month comparison states."""

    UNAVAILABLE = "unavailable"
    FROM_ZERO = "from_zero"
    STABLE = "stable"
    GROWTH = "growth"
    DECLINE = "decline"


class ForecastReliability(str, Enum):
    """Business-facing explanatory-power categories for forecasts."""

    UNAVAILABLE = "unavailable"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class RevenueKPIs(TypedDict, total=False):
    total_revenue: float
    avg_order_value: float
    mom_growth_pct: float | None
    mom_growth_status: str
    current_month: str | None
    previous_month: str | None
    current_month_revenue: float
    previous_month_revenue: float | None
    total_won_orders: int


class SalesKPIs(TypedDict, total=False):
    win_rate_pct: float
    won_orders: int
    lost_orders: int
    churned_orders: int
    churned_order_rate_pct: float
    top_account_manager: str | None
    top_account_manager_revenue: float


class ProductKPIs(TypedDict, total=False):
    product_revenue: dict[str, float]
    product_mix_pct: dict[str, float]
    units_sold: dict[str, int]
    top_product: str | None


class RegionKPIs(TypedDict, total=False):
    regional_revenue: dict[str, float]
    regional_avg_order_value: dict[str, float]
    regional_won_orders: dict[str, int]
    top_region: str | None


class TrendKPIs(TypedDict, total=False):
    monthly_revenue: list[dict[str, Any]]
    quarterly_revenue: list[dict[str, Any]]
    trend_slope: float
    trend_direction: str
    trend_direction_code: str


class AnalysisMeta(TypedDict, total=False):
    total_customers: int
    active_customers: int
    total_orders: int
    date_range: str
    generated_at: str


class KPIBundle(TypedDict, total=False):
    """Type-safe public KPI result returned by the analysis pipeline."""

    revenue: RevenueKPIs
    sales: SalesKPIs
    products: ProductKPIs
    regions: RegionKPIs
    trends: TrendKPIs
    validation: dict[str, Any]
    source_validation: dict[str, Any]
    filters: dict[str, Any]
    meta: AnalysisMeta


@dataclass(frozen=True)
class DecisionThresholds:
    """Threshold configuration used across all business-facing layers."""

    revenue_sharp_decline_pct: float = -10.0
    revenue_decline_pct: float = 0.0

    win_rate_critical_pct: float = 40.0
    win_rate_warning_pct: float = 55.0

    churned_order_warning_pct: float = 10.0
    churned_order_critical_pct: float = 15.0

    product_concentration_pct: float = 60.0


DEFAULT_THRESHOLDS = DecisionThresholds()

STABLE_TREND_TOLERANCE = 0.01
FORECAST_LOW_R2_THRESHOLD = 0.10
FORECAST_MODERATE_R2_THRESHOLD = 0.40


def classify_trend(
    slope: float,
    average_monthly_revenue: float,
) -> TrendDirection:
    """Classify a linear revenue slope using the shared tolerance rule."""

    tolerance = (
        average_monthly_revenue
        * STABLE_TREND_TOLERANCE
    )

    if slope > tolerance:
        return TrendDirection.GROWING

    if slope < -tolerance:
        return TrendDirection.DECLINING

    return TrendDirection.STABLE
