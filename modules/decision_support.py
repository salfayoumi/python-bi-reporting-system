"""
modules/decision_support.py

Runs configurable rule-based business logic on KPI results.

Business rules are evaluated once into language-independent InsightSpec
objects. Localization happens separately so English and Turkish reports
cannot accidentally execute different business logic.
"""

from dataclasses import dataclass, field
from typing import Any, Literal

from modules.domain import (
    KPIBundle,
    DEFAULT_THRESHOLDS,
    DecisionThresholds,
)
from modules.i18n import (
    DEFAULT_LANGUAGE,
    normalize_language,
    translate,
)


Severity = Literal["critical", "warning", "info", "good"]

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
class InsightSpec:
    """Language-independent representation of one business finding."""

    category_key: str
    severity: Severity
    title_key: str
    detail_key: str
    action_key: str
    detail_params: dict[str, Any] = field(default_factory=dict)
    priority_adjustment: int = 0
    extra_detail_keys: tuple[tuple[str, dict[str, Any]], ...] = ()


@dataclass(frozen=True)
class Insight:
    """Localized, user-facing business insight."""

    category: str
    severity: Severity
    title: str
    detail: str
    action: str
    priority: int


def _priority(
    severity: Severity,
    adjustment: int = 0,
) -> int:
    return SEVERITY_PRIORITY[severity] + adjustment


def _revenue_spec(
    kpis: KPIBundle,
    thresholds: DecisionThresholds,
) -> InsightSpec:
    revenue = kpis["revenue"]
    status = revenue.get("mom_growth_status", "unavailable")
    growth = revenue.get("mom_growth_pct")

    if status == "unavailable":
        return InsightSpec(
            "category.revenue",
            "info",
            "revenue.unavailable.title",
            "revenue.unavailable.detail",
            "revenue.unavailable.action",
        )

    if status == "from_zero":
        return InsightSpec(
            "category.revenue",
            "good",
            "revenue.from_zero.title",
            "revenue.from_zero.detail",
            "revenue.from_zero.action",
        )

    if growth is None:
        raise ValueError(
            "mom_growth_pct cannot be None when "
            f"mom_growth_status is {status!r}."
        )

    if growth < thresholds.revenue_sharp_decline_pct:
        return InsightSpec(
            "category.revenue",
            "critical",
            "revenue.sharp_decline.title",
            "revenue.sharp_decline.detail",
            "revenue.sharp_decline.action",
            {"value": growth},
            10,
        )

    if growth < thresholds.revenue_decline_pct:
        return InsightSpec(
            "category.revenue",
            "warning",
            "revenue.decline.title",
            "revenue.decline.detail",
            "revenue.decline.action",
            {"value": growth},
            10,
        )

    if growth == thresholds.revenue_decline_pct:
        return InsightSpec(
            "category.revenue",
            "info",
            "revenue.stable.title",
            "revenue.stable.detail",
            "revenue.stable.action",
        )

    return InsightSpec(
        "category.revenue",
        "good",
        "revenue.growth.title",
        "revenue.growth.detail",
        "revenue.growth.action",
        {"value": growth},
    )


def _sales_spec(
    kpis: KPIBundle,
    thresholds: DecisionThresholds,
) -> InsightSpec:
    win_rate = kpis["sales"]["win_rate_pct"]

    if win_rate < thresholds.win_rate_critical_pct:
        return InsightSpec(
            "category.sales",
            "critical",
            "sales.low.title",
            "sales.low.detail",
            "sales.low.action",
            {
                "value": win_rate,
                "target": thresholds.win_rate_warning_pct,
            },
        )

    if win_rate < thresholds.win_rate_warning_pct:
        return InsightSpec(
            "category.sales",
            "warning",
            "sales.below_target.title",
            "sales.below_target.detail",
            "sales.below_target.action",
            {
                "value": win_rate,
                "target": thresholds.win_rate_warning_pct,
            },
        )

    return InsightSpec(
        "category.sales",
        "good",
        "sales.healthy.title",
        "sales.healthy.detail",
        "sales.healthy.action",
        {"value": win_rate},
    )


def _order_status_spec(
    kpis: KPIBundle,
    thresholds: DecisionThresholds,
) -> InsightSpec:
    rate = kpis["sales"].get("churned_order_rate_pct")

    if rate is None:
        raise KeyError("sales.churned_order_rate_pct is required")

    if rate > thresholds.churned_order_critical_pct:
        return InsightSpec(
            "category.retention",
            "critical",
            "retention.high.title",
            "retention.high.detail",
            "retention.high.action",
            {"value": rate},
            5,
        )

    if rate > thresholds.churned_order_warning_pct:
        return InsightSpec(
            "category.retention",
            "warning",
            "retention.elevated.title",
            "retention.elevated.detail",
            "retention.elevated.action",
            {"value": rate},
            5,
        )

    return InsightSpec(
        "category.retention",
        "good",
        "retention.target.title",
        "retention.target.detail",
        "retention.target.action",
        {"value": rate},
    )


def _product_spec(
    kpis: KPIBundle,
    thresholds: DecisionThresholds,
) -> InsightSpec:
    product_mix = kpis["products"].get("product_mix_pct", {})

    if not product_mix:
        return InsightSpec(
            "category.product",
            "info",
            "product.unavailable.title",
            "product.unavailable.detail",
            "product.unavailable.action",
        )

    top_product = max(product_mix, key=product_mix.get)
    share = product_mix[top_product]

    if share > thresholds.product_concentration_pct:
        return InsightSpec(
            "category.product",
            "warning",
            "product.concentrated.title",
            "product.concentrated.detail",
            "product.concentrated.action",
            {"product": top_product, "share": share},
        )

    return InsightSpec(
        "category.product",
        "good",
        "product.diversified.title",
        "product.diversified.detail",
        "product.diversified.action",
        {"product": top_product, "share": share},
    )


def _region_spec(kpis: KPIBundle) -> InsightSpec | None:
    regions = kpis["regions"]
    revenue = regions.get("regional_revenue", {})
    average = regions.get("regional_avg_order_value", {})

    if not revenue:
        return None

    top_revenue_region = max(revenue, key=revenue.get)
    extra: list[tuple[str, dict[str, Any]]] = [
        (
            "region.top_revenue",
            {
                "region": top_revenue_region,
                "value": revenue[top_revenue_region],
            },
        )
    ]

    if average:
        top_average_region = max(average, key=average.get)
        extra.append(
            (
                "region.top_average",
                {
                    "region": top_average_region,
                    "value": average[top_average_region],
                },
            )
        )

    return InsightSpec(
        "category.region",
        "info",
        "region.leaders.title",
        "",
        "region.leaders.action",
        extra_detail_keys=tuple(extra),
    )


def _trend_spec(kpis: KPIBundle) -> InsightSpec:
    trends = kpis["trends"]
    revenue = kpis["revenue"]
    direction = trends.get("trend_direction_code", "stable")
    slope = trends["trend_slope"]

    if direction == "growing":
        severity: Severity = "good"
        title_key = "trend.growing.title"
        detail_key = "trend.growing.detail"
        action_key = "trend.growing.action"
    elif direction == "declining":
        severity = "warning"
        title_key = "trend.declining.title"
        detail_key = "trend.declining.detail"
        action_key = "trend.declining.action"
    else:
        severity = "info"
        title_key = "trend.stable.title"
        detail_key = "trend.stable.detail"
        action_key = "trend.stable.action"

    extras: list[tuple[str, dict[str, Any]]] = [
        ("trend.horizon.base", {})
    ]

    mom_growth = revenue.get("mom_growth_pct")
    mom_status = revenue.get("mom_growth_status")

    if (
        mom_growth is not None
        and mom_status in {"growth", "decline", "stable"}
    ):
        extras.append(
            ("trend.horizon.mom", {"value": mom_growth})
        )

    return InsightSpec(
        "category.trend",
        severity,
        title_key,
        detail_key,
        action_key,
        {"value": slope},
        extra_detail_keys=tuple(extras),
    )


def evaluate_rules(
    kpis: KPIBundle,
    thresholds: DecisionThresholds = DEFAULT_THRESHOLDS,
) -> list[InsightSpec]:
    """Evaluate all business rules once without localizing text."""

    specs = [
        _revenue_spec(kpis, thresholds),
        _sales_spec(kpis, thresholds),
        _order_status_spec(kpis, thresholds),
        _product_spec(kpis, thresholds),
        _trend_spec(kpis),
    ]

    regional = _region_spec(kpis)
    if regional is not None:
        specs.append(regional)

    return sorted(
        specs,
        key=lambda item: _priority(
            item.severity,
            item.priority_adjustment,
        ),
        reverse=True,
    )


def localize_insights(
    specs: list[InsightSpec],
    language: str = DEFAULT_LANGUAGE,
) -> list[Insight]:
    """Render language-independent insight specs in one language."""

    language = normalize_language(language)
    insights: list[Insight] = []

    for spec in specs:
        if spec.detail_key:
            detail_parts = [
                translate(
                    spec.detail_key,
                    language,
                    **spec.detail_params,
                )
            ]
        else:
            detail_parts = []

        for key, params in spec.extra_detail_keys:
            detail_parts.append(
                translate(key, language, **params)
            )

        insights.append(
            Insight(
                category=translate(spec.category_key, language),
                severity=spec.severity,
                title=translate(spec.title_key, language),
                detail=" ".join(detail_parts),
                action=translate(spec.action_key, language),
                priority=_priority(
                    spec.severity,
                    spec.priority_adjustment,
                ),
            )
        )

    return insights


def analyze(
    kpis: KPIBundle,
    language: str = DEFAULT_LANGUAGE,
    thresholds: DecisionThresholds = DEFAULT_THRESHOLDS,
) -> list[Insight]:
    """Compatibility wrapper: evaluate once and localize one language."""

    return localize_insights(
        evaluate_rules(kpis, thresholds),
        language,
    )


def format_report(
    insights: list[Insight],
    language: str = DEFAULT_LANGUAGE,
) -> str:
    """Convert localized insight objects into a terminal report."""

    language = normalize_language(language)

    lines = [
        "=" * 60,
        f"  {translate('report.decision_support', language)}",
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
                f"{icon}  [{insight.category}] {insight.title}",
                (
                    f"   {translate('report.detail', language)} : "
                    f"{insight.detail}"
                ),
                (
                    f"   {translate('report.action', language)} : "
                    f"{insight.action}"
                ),
                "",
            ]
        )

    return "\n".join(lines)
