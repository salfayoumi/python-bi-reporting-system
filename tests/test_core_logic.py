import pandas as pd

from modules.forecast import prepare_monthly_revenue, build_linear_forecast
from modules.kpi_engine import revenue_kpis, trend_analysis
from modules.segment_analysis import summarize_segment_performance


def _order(month, amount, status="Won"):
    date = pd.Timestamp(f"{month}-15")
    return {
        "order_id": month, "customer_id": "C1", "order_date": date,
        "month": month, "quarter": f"{date.year}-Q{date.quarter}",
        "status": status, "product": "P", "region": "R",
        "account_manager": "A", "quantity": 1, "total_amount": amount,
        "segment": "SMB",
    }


def test_missing_months_are_preserved():
    orders = pd.DataFrame([_order("2024-01", 100), _order("2024-03", 300)])
    monthly = trend_analysis(orders)["monthly_revenue"]
    assert monthly == [
        {"month": "2024-01", "revenue": 100.0},
        {"month": "2024-02", "revenue": 0.0},
        {"month": "2024-03", "revenue": 300.0},
    ]


def test_mom_unavailable_for_one_month():
    result = revenue_kpis(pd.DataFrame([_order("2024-01", 100)]))
    assert result["mom_growth_pct"] is None
    assert result["mom_growth_status"] == "unavailable"


def test_growth_from_zero_is_not_stable():
    orders = pd.DataFrame([_order("2024-01", 10, "Lost"), _order("2024-02", 100)])
    result = revenue_kpis(orders)
    assert result["mom_growth_pct"] is None
    assert result["mom_growth_status"] == "from_zero"


def test_constant_series_r_squared_is_not_perfect():
    result = build_linear_forecast([
        {"month": "2024-01", "revenue": 100},
        {"month": "2024-02", "revenue": 100},
    ])
    assert result["model"]["r_squared_interpretable"] is False
    assert result["model"]["r_squared"] == 0.0


def test_empty_segment_not_selected_as_best_rate():
    summary = summarize_segment_performance({
        "Empty": {
            "total_revenue": 0.0,
            "revenue_per_active_customer": None,
            "win_rate_pct": None,
            "churned_order_rate_pct": None,
        },
        "SMB": {
            "total_revenue": 100.0,
            "revenue_per_active_customer": 50.0,
            "win_rate_pct": 60.0,
            "churned_order_rate_pct": 20.0,
        },
    })
    assert summary["lowest_churn_rate_segment"] == "SMB"
