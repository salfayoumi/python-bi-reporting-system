from pathlib import Path

import pandas as pd
import pytest

from modules.decision_support import (
    DecisionThresholds,
    evaluate_rules,
    localize_insights,
)
from modules.i18n import TRANSLATIONS
from modules.kpi_engine import (
    compute_analysis,
    load_data,
    validate_data,
)
from modules.visualizer import _resolve_orders_data


def _customers():
    return pd.DataFrame(
        [
            {
                "customer_id": "C1",
                "company_name": "One",
                "region": "R",
                "segment": "SMB",
                "since": pd.Timestamp("2024-01-01"),
                "account_manager": "A",
            },
            {
                "customer_id": "C2",
                "company_name": "Two",
                "region": "R",
                "segment": "SMB",
                "since": pd.Timestamp("2024-01-01"),
                "account_manager": "A",
            },
        ]
    )


def _orders():
    return pd.DataFrame(
        [
            {
                "order_id": "O1",
                "customer_id": "C1",
                "region": "R",
                "segment": "SMB",
                "account_manager": "A",
                "product": "P",
                "quantity": 2,
                "unit_price": 50.0,
                "total_amount": 100.0,
                "status": "Won",
                "order_date": pd.Timestamp("2024-02-15"),
                "month": "2024-02",
                "quarter": "2024-Q1",
                "year": 2024,
            }
        ]
    )


def test_analysis_result_separates_metrics_from_data():
    result = compute_analysis(
        orders=_orders(),
        customers=_customers(),
        product="P",
        print_validation=False,
    )

    assert "_data" not in result.kpis
    assert len(result.orders) == 1
    assert len(result.customers) == 2
    assert result.kpis["meta"]["total_customers"] == 2
    assert result.kpis["meta"]["active_customers"] == 1


def test_validator_restores_referential_and_business_checks():
    orders = _orders().copy()
    customers = _customers().copy()

    orders.loc[0, "customer_id"] = "MISSING"
    orders.loc[0, "total_amount"] = 999.0
    orders.loc[0, "month"] = "2024-03"
    orders.loc[0, "quarter"] = "2024-Q2"
    orders.loc[0, "year"] = 2023

    report = validate_data(orders=orders, customers=customers)

    assert report["orders"]["orphan_customer_references"] == 1
    assert report["orders"]["total_amount_mismatch"] == 1
    assert report["orders"]["month_mismatch"] == 1
    assert report["orders"]["quarter_mismatch"] == 1
    assert report["orders"]["year_mismatch"] == 1
    assert report["passed"] is False


def test_validator_detects_order_before_customer_registration():
    orders = _orders().copy()
    customers = _customers().copy()
    customers.loc[0, "since"] = pd.Timestamp("2024-03-01")

    report = validate_data(orders=orders, customers=customers)

    assert (
        report["orders"]["orders_before_customer_registration"]
        == 1
    )


def test_missing_files_raise_user_friendly_value_error(tmp_path):
    with pytest.raises(ValueError, match="could not be found"):
        load_data(
            orders_path=tmp_path / "orders.csv",
            customers_path=tmp_path / "customers.csv",
        )


def test_order_charts_require_explicit_filtered_data():
    with pytest.raises(ValueError, match="must be supplied explicitly"):
        _resolve_orders_data(None)


def test_all_translation_keys_have_language_parity():
    assert set(TRANSLATIONS["en"]) == set(TRANSLATIONS["tr"])


def test_custom_threshold_is_reflected_in_localized_text():
    kpis = {
        "revenue": {
            "mom_growth_pct": 5.0,
            "mom_growth_status": "growth",
        },
        "sales": {
            "win_rate_pct": 60.0,
            "churned_order_rate_pct": 5.0,
        },
        "products": {
            "product_mix_pct": {"P": 50.0, "Q": 50.0},
        },
        "regions": {
            "regional_revenue": {},
            "regional_avg_order_value": {},
        },
        "trends": {
            "trend_direction_code": "stable",
            "trend_slope": 0.0,
        },
    }

    thresholds = DecisionThresholds(
        win_rate_warning_pct=70.0,
    )

    specs = evaluate_rules(
        kpis,
        thresholds=thresholds,
    )
    insights = localize_insights(specs, "en")

    sales = next(
        item
        for item in insights
        if item.category == "Sales"
    )

    assert "70%" in sales.detail


def test_business_rules_can_be_localized_without_reevaluation():
    kpis = {
        "revenue": {
            "mom_growth_pct": 5.0,
            "mom_growth_status": "growth",
        },
        "sales": {
            "win_rate_pct": 75.0,
            "churned_order_rate_pct": 5.0,
        },
        "products": {
            "product_mix_pct": {"P": 50.0, "Q": 50.0},
        },
        "regions": {
            "regional_revenue": {},
            "regional_avg_order_value": {},
        },
        "trends": {
            "trend_direction_code": "stable",
            "trend_slope": 0.0,
        },
    }

    specs = evaluate_rules(kpis)

    en = localize_insights(specs, "en")
    tr = localize_insights(specs, "tr")

    assert [item.severity for item in en] == [
        item.severity for item in tr
    ]
    assert [item.priority for item in en] == [
        item.priority for item in tr
    ]
