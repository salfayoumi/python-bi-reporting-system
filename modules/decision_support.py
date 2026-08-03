"""
modules/decision_support.py

Runs configurable rule-based and threshold-based decision logic
on top of KPI results.

Produces localized, prioritized, and actionable business insights.
"""

from dataclasses import dataclass
from typing import Callable, Literal

from modules.i18n import (
    DEFAULT_LANGUAGE,
    normalize_language,
    translate,
)


Severity = Literal[
    "critical",
    "warning",
    "info",
    "good",
]

Translator = Callable[..., str]


SEVERITY_PRIORITY = {
    "critical": 100,
    "warning": 75,
    "info": 50,
    "good": 25,
}

REPORT_ICONS = {
    "critical": "🔴",
    "warning": "🟡",
    "info": "🔵",
    "good": "🟢",
}


@dataclass(frozen=True)
class DecisionThresholds:
    """Threshold configuration used by decision-support rules."""

    revenue_sharp_decline_pct: float = -10.0
    revenue_decline_pct: float = 0.0

    win_rate_critical_pct: float = 40.0
    win_rate_warning_pct: float = 55.0

    churn_warning_pct: float = 10.0
    churn_critical_pct: float = 15.0

    product_concentration_pct: float = 60.0


DEFAULT_THRESHOLDS = DecisionThresholds()


@dataclass(frozen=True)
class Insight:
    """Represents one localized and actionable business insight."""

    category: str
    severity: Severity
    title: str
    detail: str
    action: str
    priority: int


def _create_insight(
    *,
    category: str,
    severity: Severity,
    title: str,
    detail: str,
    action: str,
    priority_adjustment: int = 0,
) -> Insight:
    """Create an insight with a consistent priority score."""

    priority = (
        SEVERITY_PRIORITY[severity]
        + priority_adjustment
    )

    return Insight(
        category=category,
        severity=severity,
        title=title,
        detail=detail,
        action=action,
        priority=priority,
    )


def _analyze_revenue(
    kpis: dict,
    translator: Translator,
    thresholds: DecisionThresholds,
) -> Insight:
    """Evaluate month-over-month revenue performance."""

    mom_growth = kpis["revenue"]["mom_growth_pct"]

    if (
        mom_growth
        < thresholds.revenue_sharp_decline_pct
    ):
        return _create_insight(
            category=translator(
                "category.revenue"
            ),
            severity="critical",
            title=translator(
                "revenue.sharp_decline.title"
            ),
            detail=translator(
                "revenue.sharp_decline.detail",
                value=mom_growth,
            ),
            action=translator(
                "revenue.sharp_decline.action"
            ),
            priority_adjustment=10,
        )

    if mom_growth < thresholds.revenue_decline_pct:
        return _create_insight(
            category=translator(
                "category.revenue"
            ),
            severity="warning",
            title=translator(
                "revenue.decline.title"
            ),
            detail=translator(
                "revenue.decline.detail",
                value=mom_growth,
            ),
            action=translator(
                "revenue.decline.action"
            ),
            priority_adjustment=10,
        )

    if mom_growth == thresholds.revenue_decline_pct:
        return _create_insight(
            category=translator(
                "category.revenue"
            ),
            severity="info",
            title=translator(
                "revenue.stable.title"
            ),
            detail=translator(
                "revenue.stable.detail"
            ),
            action=translator(
                "revenue.stable.action"
            ),
        )

    return _create_insight(
        category=translator(
            "category.revenue"
        ),
        severity="good",
        title=translator(
            "revenue.growth.title"
        ),
        detail=translator(
            "revenue.growth.detail",
            value=mom_growth,
        ),
        action=translator(
            "revenue.growth.action"
        ),
    )


def _analyze_sales(
    kpis: dict,
    translator: Translator,
    thresholds: DecisionThresholds,
) -> Insight:
    """Evaluate the sales win rate."""

    win_rate = kpis["sales"]["win_rate_pct"]

    if win_rate < thresholds.win_rate_critical_pct:
        return _create_insight(
            category=translator(
                "category.sales"
            ),
            severity="critical",
            title=translator(
                "sales.low.title"
            ),
            detail=translator(
                "sales.low.detail",
                value=win_rate,
            ),
            action=translator(
                "sales.low.action"
            ),
        )

    if win_rate < thresholds.win_rate_warning_pct:
        return _create_insight(
            category=translator(
                "category.sales"
            ),
            severity="warning",
            title=translator(
                "sales.below_target.title"
            ),
            detail=translator(
                "sales.below_target.detail",
                value=win_rate,
            ),
            action=translator(
                "sales.below_target.action"
            ),
        )

    return _create_insight(
        category=translator(
            "category.sales"
        ),
        severity="good",
        title=translator(
            "sales.healthy.title"
        ),
        detail=translator(
            "sales.healthy.detail",
            value=win_rate,
        ),
        action=translator(
            "sales.healthy.action"
        ),
    )


def _analyze_retention(
    kpis: dict,
    translator: Translator,
    thresholds: DecisionThresholds,
) -> Insight:
    """Evaluate the churn-status rate."""

    churn_rate = kpis["sales"]["churn_rate_pct"]

    if churn_rate > thresholds.churn_critical_pct:
        return _create_insight(
            category=translator(
                "category.retention"
            ),
            severity="critical",
            title=translator(
                "retention.high.title"
            ),
            detail=translator(
                "retention.high.detail",
                value=churn_rate,
            ),
            action=translator(
                "retention.high.action"
            ),
            priority_adjustment=5,
        )

    if churn_rate > thresholds.churn_warning_pct:
        return _create_insight(
            category=translator(
                "category.retention"
            ),
            severity="warning",
            title=translator(
                "retention.elevated.title"
            ),
            detail=translator(
                "retention.elevated.detail",
                value=churn_rate,
            ),
            action=translator(
                "retention.elevated.action"
            ),
            priority_adjustment=5,
        )

    return _create_insight(
        category=translator(
            "category.retention"
        ),
        severity="good",
        title=translator(
            "retention.target.title"
        ),
        detail=translator(
            "retention.target.detail",
            value=churn_rate,
        ),
        action=translator(
            "retention.target.action"
        ),
    )


def _analyze_product(
    kpis: dict,
    translator: Translator,
    thresholds: DecisionThresholds,
) -> Insight:
    """Evaluate product revenue concentration."""

    product_mix = kpis["products"].get(
        "product_mix_pct",
        {},
    )

    if not product_mix:
        return _create_insight(
            category=translator(
                "category.product"
            ),
            severity="info",
            title=translator(
                "product.unavailable.title"
            ),
            detail=translator(
                "product.unavailable.detail"
            ),
            action=translator(
                "product.unavailable.action"
            ),
        )

    top_product = max(
        product_mix,
        key=product_mix.get,
    )

    top_product_share = product_mix[
        top_product
    ]

    if (
        top_product_share
        > thresholds.product_concentration_pct
    ):
        return _create_insight(
            category=translator(
                "category.product"
            ),
            severity="warning",
            title=translator(
                "product.concentrated.title"
            ),
            detail=translator(
                "product.concentrated.detail",
                product=top_product,
                share=top_product_share,
            ),
            action=translator(
                "product.concentrated.action"
            ),
        )

    return _create_insight(
        category=translator(
            "category.product"
        ),
        severity="good",
        title=translator(
            "product.diversified.title"
        ),
        detail=translator(
            "product.diversified.detail",
            product=top_product,
            share=top_product_share,
        ),
        action=translator(
            "product.diversified.action"
        ),
    )


def _analyze_region(
    kpis: dict,
    translator: Translator,
) -> Insight | None:
    """Identify the leading regions by revenue and order value."""

    regions = kpis["regions"]

    regional_revenue = regions.get(
        "regional_revenue",
        {},
    )

    regional_avg_order_value = regions.get(
        "regional_avg_order_value",
        {},
    )

    if not regional_revenue:
        return None

    top_revenue_region = max(
        regional_revenue,
        key=regional_revenue.get,
    )

    top_region_revenue = regional_revenue[
        top_revenue_region
    ]

    detail_parts = [
        translator(
            "region.top_revenue",
            region=top_revenue_region,
            value=top_region_revenue,
        )
    ]

    if regional_avg_order_value:
        top_avg_region = max(
            regional_avg_order_value,
            key=regional_avg_order_value.get,
        )

        top_avg_value = (
            regional_avg_order_value[
                top_avg_region
            ]
        )

        detail_parts.append(
            translator(
                "region.top_average",
                region=top_avg_region,
                value=top_avg_value,
            )
        )

    return _create_insight(
        category=translator(
            "category.region"
        ),
        severity="info",
        title=translator(
            "region.leaders.title"
        ),
        detail=" ".join(detail_parts),
        action=translator(
            "region.leaders.action"
        ),
    )


def _analyze_trend(
    kpis: dict,
    translator: Translator,
) -> Insight:
    """Evaluate the long-term revenue trend."""

    trends = kpis["trends"]

    trend_direction = trends[
        "trend_direction"
    ]

    trend_slope = trends[
        "trend_slope"
    ]

    if "Growing" in trend_direction:
        return _create_insight(
            category=translator(
                "category.trend"
            ),
            severity="good",
            title=translator(
                "trend.growing.title"
            ),
            detail=translator(
                "trend.growing.detail",
                value=trend_slope,
            ),
            action=translator(
                "trend.growing.action"
            ),
        )

    if "Declining" in trend_direction:
        return _create_insight(
            category=translator(
                "category.trend"
            ),
            severity="warning",
            title=translator(
                "trend.declining.title"
            ),
            detail=translator(
                "trend.declining.detail",
                value=trend_slope,
            ),
            action=translator(
                "trend.declining.action"
            ),
        )

    return _create_insight(
        category=translator(
            "category.trend"
        ),
        severity="info",
        title=translator(
            "trend.stable.title"
        ),
        detail=translator(
            "trend.stable.detail",
            value=trend_slope,
        ),
        action=translator(
            "trend.stable.action"
        ),
    )


def analyze(
    kpis: dict,
    language: str = DEFAULT_LANGUAGE,
    thresholds: DecisionThresholds = DEFAULT_THRESHOLDS,
) -> list[Insight]:
    """
    Convert KPI results into localized business insights.

    Independent business rules generate insights, which are then
    sorted from highest to lowest priority.
    """

    normalized_language = normalize_language(
        language
    )

    def translator(
        key: str,
        **kwargs,
    ) -> str:
        return translate(
            key,
            normalized_language,
            **kwargs,
        )

    insights = [
        _analyze_revenue(
            kpis,
            translator,
            thresholds,
        ),
        _analyze_sales(
            kpis,
            translator,
            thresholds,
        ),
        _analyze_retention(
            kpis,
            translator,
            thresholds,
        ),
        _analyze_product(
            kpis,
            translator,
            thresholds,
        ),
        _analyze_trend(
            kpis,
            translator,
        ),
    ]

    regional_insight = _analyze_region(
        kpis,
        translator,
    )

    if regional_insight is not None:
        insights.append(
            regional_insight
        )

    return sorted(
        insights,
        key=lambda insight: (
            insight.priority
        ),
        reverse=True,
    )


def format_report(
    insights: list[Insight],
    language: str = DEFAULT_LANGUAGE,
) -> str:
    """Convert insight objects into a localized terminal report."""

    normalized_language = normalize_language(
        language
    )

    def translator(key: str) -> str:
        return translate(
            key,
            normalized_language,
        )

    lines = [
        "=" * 60,
        (
            f"  "
            f"{translator('report.decision_support')}"
        ),
        "=" * 60,
        "",
    ]

    for insight in insights:
        icon = REPORT_ICONS.get(
            insight.severity,
            REPORT_ICONS["info"],
        )

        lines.extend(
            [
                (
                    f"{icon}  "
                    f"[{insight.category}] "
                    f"{insight.title}"
                ),
                (
                    f"   "
                    f"{translator('report.detail')} : "
                    f"{insight.detail}"
                ),
                (
                    f"   "
                    f"{translator('report.action')} : "
                    f"{insight.action}"
                ),
                "",
            ]
        )

    return "\n".join(lines)