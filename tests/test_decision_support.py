from modules.decision_support import (
    DecisionThresholds,
    analyze,
)


BASE_KPIS = {
    "revenue": {
        "mom_growth_pct": -15.0,
        "mom_growth_status": "decline",
    },
    "sales": {
        "win_rate_pct": 18.0,
        "churned_order_rate_pct": 22.0,
        "churned_order_rate_pct": 22.0,
    },
    "products": {
        "product_mix_pct": {
            "CRM": 65.0,
            "Analytics": 20.0,
            "Support": 15.0,
        },
    },
    "regions": {
        "regional_revenue": {
            "Istanbul": 250000,
            "Ankara": 150000,
            "Izmir": 100000,
        },
        "regional_avg_order_value": {
            "Istanbul": 5200,
            "Ankara": 4700,
            "Izmir": 4300,
        },
    },
    "trends": {
        "trend_direction": "↓ Declining",
        "trend_direction_code": "declining",
        "trend_slope": -1200.0,
    },
}


def find_insight(insights, category):
    return next(
        (
            insight
            for insight in insights
            if insight.category.lower() == category.lower()
        ),
        None,
    )


def test_default_thresholds():
    """Default thresholds should detect all expected business issues."""

    insights = analyze(BASE_KPIS, language="en")

    assert len(insights) == 6

    assert find_insight(insights, "Revenue") is not None
    assert find_insight(insights, "Sales") is not None
    assert find_insight(insights, "Order Status") is not None
    assert find_insight(insights, "Product") is not None
    assert find_insight(insights, "Region") is not None
    assert find_insight(insights, "Trend") is not None


def test_custom_thresholds():
    """Relaxed thresholds should reduce the number of warnings."""

    relaxed = DecisionThresholds(
        revenue_sharp_decline_pct=-30.0,
        revenue_decline_pct=-20.0,
        win_rate_critical_pct=10.0,
        win_rate_warning_pct=15.0,
        churned_order_warning_pct=30.0,
        churned_order_critical_pct=40.0,
        product_concentration_pct=80.0,
    )

    insights = analyze(
        BASE_KPIS,
        language="en",
        thresholds=relaxed,
    )

    revenue = find_insight(insights, "Revenue")
    sales = find_insight(insights, "Sales")
    retention = find_insight(insights, "Order Status")
    product = find_insight(insights, "Product")

    assert revenue.severity == "good"
    assert sales.severity == "good"
    assert retention.severity == "good"
    assert product.severity == "good"


def test_priority_sorting():
    """Insights should already be sorted by priority."""

    insights = analyze(BASE_KPIS, language="en")

    priorities = [i.priority for i in insights]

    assert priorities == sorted(
        priorities,
        reverse=True,
    )


