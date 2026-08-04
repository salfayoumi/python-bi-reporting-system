"""
modules/kpi_engine.py

Loads CRM datasets and calculates the core business KPIs used by
the dashboard, decision-support engine, visualizations, and exports.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_ORDERS_PATH = Path("data/orders.csv")
DEFAULT_CUSTOMERS_PATH = Path("data/customers.csv")

STATUS_WON = "Won"
STATUS_LOST = "Lost"
STATUS_CHURNED = "Churned"

VALID_ORDER_STATUSES = {
    STATUS_WON,
    STATUS_LOST,
    STATUS_CHURNED,
}

REQUIRED_ORDER_COLUMNS = {
    "order_id",
    "customer_id",
    "order_date",
    "month",
    "quarter",
    "status",
    "product",
    "region",
    "account_manager",
    "quantity",
    "total_amount",
}

REQUIRED_CUSTOMER_COLUMNS = {
    "customer_id",
    "since",
    "segment",
    "region",
}

STABLE_TREND_TOLERANCE = 0.01


def load_data(
    orders_path: str | Path = DEFAULT_ORDERS_PATH,
    customers_path: str | Path = DEFAULT_CUSTOMERS_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the order and customer datasets.

    Dates are parsed automatically so downstream modules can use
    datetime operations without additional conversion.
    """

    orders = pd.read_csv(
        orders_path,
        parse_dates=["order_date"],
    )

    customers = pd.read_csv(
        customers_path,
        parse_dates=["since"],
    )

    return orders, customers


def _filter_text_column(
    dataframe: pd.DataFrame,
    column: str,
    value: str | None,
) -> pd.DataFrame:
    """Filter a text column using a case-insensitive exact match."""

    if value is None:
        return dataframe

    normalized_value = value.strip().casefold()

    return dataframe[
        dataframe[column]
        .astype(str)
        .str.strip()
        .str.casefold()
        == normalized_value
    ]


def apply_filters(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    *,
    region: str | None = None,
    year: int | None = None,
    segment: str | None = None,
    product: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Apply optional filters to the CRM datasets.

    Filters use AND logic. Customers are restricted to those referenced
    by the filtered orders so downstream analyses remain consistent.
    """

    filtered_orders = orders.copy()
    filtered_customers = customers.copy()

    requested_filters = {
        "region": region,
        "year": year,
        "segment": segment,
        "product": product,
    }

    filtered_orders = _filter_text_column(
        filtered_orders,
        "region",
        region,
    )

    if region is not None:
        filtered_customers = _filter_text_column(
            filtered_customers,
            "region",
            region,
        )

    filtered_orders = _filter_text_column(
        filtered_orders,
        "segment",
        segment,
    )

    if segment is not None:
        filtered_customers = _filter_text_column(
            filtered_customers,
            "segment",
            segment,
        )

    filtered_orders = _filter_text_column(
        filtered_orders,
        "product",
        product,
    )

    if year is not None:
        order_years = pd.to_datetime(
            filtered_orders["order_date"],
            errors="coerce",
        ).dt.year

        filtered_orders = filtered_orders[
            order_years == year
        ]

    if filtered_orders.empty:
        selected_filters = ", ".join(
            f"{key}={value}"
            for key, value in requested_filters.items()
            if value is not None
        )

        raise ValueError(
            "No orders matched the selected filters"
            + (
                f": {selected_filters}."
                if selected_filters
                else "."
            )
        )

    filtered_customer_ids = set(
        filtered_orders["customer_id"]
        .dropna()
    )

    filtered_customers = filtered_customers[
        filtered_customers["customer_id"]
        .isin(filtered_customer_ids)
    ]

    if filtered_customers.empty:
        raise ValueError(
            "The selected filters produced orders but no matching "
            "customer records."
        )

    applied_filters = {
        key: value
        for key, value in requested_filters.items()
        if value is not None
    }

    return (
        filtered_orders.reset_index(drop=True),
        filtered_customers.reset_index(drop=True),
        applied_filters,
    )


def _missing_required_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
) -> list[str]:
    """Return required columns that are missing from a dataset."""

    return sorted(
        required_columns
        - set(dataframe.columns)
    )


def validate_data(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    *,
    print_report: bool = True,
) -> dict:
    """
    Validate the CRM datasets before KPI calculation.

    Critical structural problems raise ValueError. Data-quality issues
    are reported as warnings so the pipeline can continue.
    """

    if orders.empty:
        raise ValueError(
            "The orders dataset is empty."
        )

    if customers.empty:
        raise ValueError(
            "The customers dataset is empty."
        )

    missing_order_columns = (
        _missing_required_columns(
            orders,
            REQUIRED_ORDER_COLUMNS,
        )
    )

    missing_customer_columns = (
        _missing_required_columns(
            customers,
            REQUIRED_CUSTOMER_COLUMNS,
        )
    )

    if missing_order_columns:
        raise ValueError(
            "Orders dataset is missing required columns: "
            + ", ".join(
                missing_order_columns
            )
        )

    if missing_customer_columns:
        raise ValueError(
            "Customers dataset is missing required columns: "
            + ", ".join(
                missing_customer_columns
            )
        )

    order_missing_values = int(
        orders.isna().sum().sum()
    )

    customer_missing_values = int(
        customers.isna().sum().sum()
    )

    order_duplicate_rows = int(
        orders.duplicated().sum()
    )

    customer_duplicate_rows = int(
        customers.duplicated().sum()
    )

    negative_revenue = int(
        (
            pd.to_numeric(
                orders["total_amount"],
                errors="coerce",
            )
            < 0
        ).sum()
    )

    invalid_quantity = int(
        (
            pd.to_numeric(
                orders["quantity"],
                errors="coerce",
            )
            <= 0
        ).sum()
    )

    unknown_statuses = sorted(
        set(
            orders["status"]
            .dropna()
            .astype(str)
        )
        - VALID_ORDER_STATUSES
    )

    unknown_status_count = int(
        orders["status"]
        .isin(
            unknown_statuses
        )
        .sum()
    )

    invalid_order_dates = int(
        pd.to_datetime(
            orders["order_date"],
            errors="coerce",
        )
        .isna()
        .sum()
    )

    invalid_customer_dates = int(
        pd.to_datetime(
            customers["since"],
            errors="coerce",
        )
        .isna()
        .sum()
    )

    report = {
        "customers": {
            "rows": len(customers),
            "columns": len(customers.columns),
            "missing_values": (
                customer_missing_values
            ),
            "duplicate_rows": (
                customer_duplicate_rows
            ),
            "invalid_dates": (
                invalid_customer_dates
            ),
        },
        "orders": {
            "rows": len(orders),
            "columns": len(orders.columns),
            "missing_values": (
                order_missing_values
            ),
            "duplicate_rows": (
                order_duplicate_rows
            ),
            "negative_revenue": (
                negative_revenue
            ),
            "invalid_quantity": (
                invalid_quantity
            ),
            "unknown_status_count": (
                unknown_status_count
            ),
            "unknown_statuses": (
                unknown_statuses
            ),
            "invalid_dates": (
                invalid_order_dates
            ),
        },
    }

    warning_count = sum(
        [
            customer_missing_values,
            customer_duplicate_rows,
            invalid_customer_dates,
            order_missing_values,
            order_duplicate_rows,
            negative_revenue,
            invalid_quantity,
            unknown_status_count,
            invalid_order_dates,
        ]
    )

    report["passed"] = (
        warning_count == 0
    )

    if print_report:
        print("\n" + "=" * 55)
        print("  DATA VALIDATION REPORT")
        print("=" * 55)

        print("\nCustomers Dataset")
        print("-" * 55)
        print(
            f"   Rows              : "
            f"{len(customers):,}"
        )
        print(
            f"   Columns           : "
            f"{len(customers.columns)}"
        )
        print(
            f"   Missing Values    : "
            f"{customer_missing_values}"
        )
        print(
            f"   Duplicate Rows    : "
            f"{customer_duplicate_rows}"
        )
        print(
            f"   Invalid Dates     : "
            f"{invalid_customer_dates}"
        )

        print("\nOrders Dataset")
        print("-" * 55)
        print(
            f"   Rows              : "
            f"{len(orders):,}"
        )
        print(
            f"   Columns           : "
            f"{len(orders.columns)}"
        )
        print(
            f"   Missing Values    : "
            f"{order_missing_values}"
        )
        print(
            f"   Duplicate Rows    : "
            f"{order_duplicate_rows}"
        )
        print(
            f"   Negative Revenue  : "
            f"{negative_revenue}"
        )
        print(
            f"   Invalid Quantity  : "
            f"{invalid_quantity}"
        )
        print(
            f"   Unknown Status    : "
            f"{unknown_status_count}"
        )
        print(
            f"   Invalid Dates     : "
            f"{invalid_order_dates}"
        )

        if unknown_statuses:
            print(
                "   Unknown Values    : "
                + ", ".join(
                    unknown_statuses
                )
            )

        print()

        if report["passed"]:
            print(
                "✓ Dataset validation completed "
                "successfully."
            )
        else:
            print(
                "⚠ Dataset validation completed "
                "with warnings."
            )

        print("=" * 55)

    return report


def _won_orders(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Return only successfully won orders."""

    return orders[
        orders["status"] == STATUS_WON
    ]


# ── 1. Revenue KPIs ───────────────────────────────────────────────────────────
def revenue_kpis(
    orders: pd.DataFrame,
) -> dict:
    """Calculate revenue-related KPIs using won orders."""

    won_orders = _won_orders(orders)

    total_revenue = won_orders[
        "total_amount"
    ].sum()

    avg_order_value = (
        won_orders["total_amount"].mean()
        if not won_orders.empty
        else 0.0
    )

    monthly_revenue = (
        won_orders.groupby("month")[
            "total_amount"
        ]
        .sum()
        .sort_index()
    )

    current_month = None
    previous_month = None

    current_month_revenue = 0.0
    previous_month_revenue = 0.0
    mom_growth = 0.0

    if not monthly_revenue.empty:
        current_month = (
            monthly_revenue.index[-1]
        )

        current_month_revenue = (
            monthly_revenue.iloc[-1]
        )

    if len(monthly_revenue) >= 2:
        previous_month = (
            monthly_revenue.index[-2]
        )

        previous_month_revenue = (
            monthly_revenue.iloc[-2]
        )

        if previous_month_revenue != 0:
            mom_growth = (
                (
                    current_month_revenue
                    - previous_month_revenue
                )
                / previous_month_revenue
                * 100
            )

    return {
        "total_revenue": round(
            total_revenue,
            2,
        ),
        "avg_order_value": round(
            avg_order_value,
            2,
        ),
        "total_won_orders": len(
            won_orders
        ),
        "current_month": current_month,
        "current_month_revenue": round(
            current_month_revenue,
            2,
        ),
        "previous_month": previous_month,
        "previous_month_revenue": round(
            previous_month_revenue,
            2,
        ),
        "mom_growth_pct": round(
            mom_growth,
            2,
        ),
    }


# ── 2. Sales KPIs ─────────────────────────────────────────────────────────────
def sales_kpis(
    orders: pd.DataFrame,
) -> dict:
    """Calculate sales-status and account-manager KPIs."""

    won_orders = _won_orders(orders)

    lost_orders = orders[
        orders["status"] == STATUS_LOST
    ]

    churned_orders = orders[
        orders["status"] == STATUS_CHURNED
    ]

    won_count = len(won_orders)
    lost_count = len(lost_orders)
    churned_count = len(churned_orders)
    total_orders = len(orders)

    closed_opportunities = (
        won_count + lost_count
    )

    win_rate = (
        won_count
        / closed_opportunities
        * 100
        if closed_opportunities
        else 0.0
    )

    churn_rate = (
        churned_count
        / total_orders
        * 100
        if total_orders
        else 0.0
    )

    account_manager_revenue = (
        won_orders.groupby(
            "account_manager"
        )["total_amount"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    if account_manager_revenue.empty:
        top_account_manager = "N/A"
        top_am_revenue = 0.0
    else:
        top_account_manager = (
            account_manager_revenue.index[0]
        )

        top_am_revenue = (
            account_manager_revenue.iloc[0]
        )

    return {
        "won_orders": won_count,
        "lost_orders": lost_count,
        "churned_orders": churned_count,
        "win_rate_pct": round(
            win_rate,
            2,
        ),
        "churn_rate_pct": round(
            churn_rate,
            2,
        ),
        "top_account_manager": (
            top_account_manager
        ),
        "top_am_revenue": round(
            top_am_revenue,
            2,
        ),
    }


# ── 3. Product KPIs ───────────────────────────────────────────────────────────
def product_kpis(
    orders: pd.DataFrame,
) -> dict:
    """Calculate product revenue, mix, and sales-volume KPIs."""

    won_orders = _won_orders(orders)

    product_revenue = (
        won_orders.groupby(
            "product"
        )["total_amount"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    product_units = (
        won_orders.groupby(
            "product"
        )["quantity"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    if product_revenue.empty:
        top_product = "N/A"

        product_mix = pd.Series(
            dtype=float
        )

    else:
        top_product = (
            product_revenue.index[0]
        )

        total_product_revenue = (
            product_revenue.sum()
        )

        if total_product_revenue != 0:
            product_mix = (
                product_revenue
                / total_product_revenue
                * 100
            ).round(2)

        else:
            product_mix = pd.Series(
                0.0,
                index=product_revenue.index,
            )

    return {
        "top_product": top_product,
        "product_revenue": (
            product_revenue
            .round(2)
            .to_dict()
        ),
        "product_mix_pct": (
            product_mix.to_dict()
        ),
        "product_units_sold": (
            product_units.to_dict()
        ),
    }


# ── 4. Regional KPIs ──────────────────────────────────────────────────────────
def regional_kpis(
    orders: pd.DataFrame,
) -> dict:
    """Calculate regional revenue and order-performance KPIs."""

    won_orders = _won_orders(orders)

    regional_revenue = (
        won_orders.groupby(
            "region"
        )["total_amount"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    regional_won_orders = (
        won_orders.groupby(
            "region"
        )
        .size()
        .sort_values(
            ascending=False
        )
    )

    regional_avg_order_value = (
        won_orders.groupby(
            "region"
        )["total_amount"]
        .mean()
        .sort_values(
            ascending=False
        )
    )

    top_region = (
        regional_revenue.index[0]
        if not regional_revenue.empty
        else "N/A"
    )

    return {
        "top_region": top_region,
        "regional_revenue": (
            regional_revenue
            .round(2)
            .to_dict()
        ),
        "regional_won_orders": (
            regional_won_orders.to_dict()
        ),
        "regional_avg_order_value": (
            regional_avg_order_value
            .round(2)
            .to_dict()
        ),
    }


# ── 5. Trend Analysis ─────────────────────────────────────────────────────────
def trend_analysis(
    orders: pd.DataFrame,
) -> dict:
    """Calculate monthly and quarterly revenue trends."""

    won_orders = _won_orders(orders)

    monthly_revenue = (
        won_orders.groupby(
            "month"
        )["total_amount"]
        .sum()
        .sort_index()
        .reset_index()
    )

    monthly_revenue.columns = [
        "month",
        "revenue",
    ]

    monthly_revenue["revenue"] = (
        monthly_revenue[
            "revenue"
        ].round(2)
    )

    quarterly_revenue = (
        won_orders.groupby(
            "quarter"
        )["total_amount"]
        .sum()
        .sort_index()
        .reset_index()
    )

    quarterly_revenue.columns = [
        "quarter",
        "revenue",
    ]

    quarterly_revenue["revenue"] = (
        quarterly_revenue[
            "revenue"
        ].round(2)
    )

    x_values = np.arange(
        len(monthly_revenue)
    )

    if len(x_values) > 1:
        slope = np.polyfit(
            x_values,
            monthly_revenue["revenue"],
            1,
        )[0]
    else:
        slope = 0.0

    average_monthly_revenue = (
        monthly_revenue[
            "revenue"
        ].mean()
        if not monthly_revenue.empty
        else 0.0
    )

    trend_tolerance = (
        average_monthly_revenue
        * STABLE_TREND_TOLERANCE
    )

    if slope > trend_tolerance:
        trend_direction = "↑ Growing"

    elif slope < -trend_tolerance:
        trend_direction = "↓ Declining"

    else:
        trend_direction = "→ Stable"

    return {
        "monthly_revenue": (
            monthly_revenue.to_dict(
                "records"
            )
        ),
        "quarterly_revenue": (
            quarterly_revenue.to_dict(
                "records"
            )
        ),
        "trend_slope": round(
            slope,
            2,
        ),
        "trend_direction": (
            trend_direction
        ),
    }


# ── Master Runner ─────────────────────────────────────────────────────────────
def compute_all_kpis(
    orders: pd.DataFrame | None = None,
    customers: pd.DataFrame | None = None,
    *,
    orders_path: str | Path = DEFAULT_ORDERS_PATH,
    customers_path: str | Path = DEFAULT_CUSTOMERS_PATH,
    region: str | None = None,
    year: int | None = None,
    segment: str | None = None,
    product: str | None = None,
    print_validation_report: bool = True,
) -> dict:
    """
    Calculate all KPI categories from full or filtered CRM data.

    DataFrames may be supplied directly. If omitted, the datasets are
    loaded from disk. Optional filters are applied before KPI calculation.
    """

    if orders is None and customers is None:
        resolved_orders, resolved_customers = load_data(
            orders_path,
            customers_path,
        )
    elif orders is None or customers is None:
        raise ValueError(
            "orders and customers must either both be provided "
            "or both be omitted."
        )
    else:
        resolved_orders = orders.copy()
        resolved_customers = customers.copy()

    validation_report = validate_data(
        resolved_orders,
        resolved_customers,
        print_report=print_validation_report,
    )

    (
        filtered_orders,
        filtered_customers,
        applied_filters,
    ) = apply_filters(
        resolved_orders,
        resolved_customers,
        region=region,
        year=year,
        segment=segment,
        product=product,
    )

    minimum_date = (
        filtered_orders["order_date"]
        .min()
        .date()
    )

    maximum_date = (
        filtered_orders["order_date"]
        .max()
        .date()
    )

    return {
        "revenue": revenue_kpis(
            filtered_orders
        ),
        "sales": sales_kpis(
            filtered_orders
        ),
        "products": product_kpis(
            filtered_orders
        ),
        "regions": regional_kpis(
            filtered_orders
        ),
        "trends": trend_analysis(
            filtered_orders
        ),
        "validation": validation_report,
        "filters": applied_filters,
        "meta": {
            "total_customers": len(
                filtered_customers
            ),
            "total_orders": len(
                filtered_orders
            ),
            "date_range": (
                f"{minimum_date} "
                f"→ {maximum_date}"
            ),
            "generated_at": (
                pd.Timestamp.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
        },
        "_data": {
            "orders": filtered_orders,
            "customers": filtered_customers,
        },
    }


if __name__ == "__main__":
    kpis = compute_all_kpis()

    printable_kpis = {
        key: value
        for key, value in kpis.items()
        if key != "_data"
    }

    print(
        json.dumps(
            printable_kpis,
            indent=2,
            default=str,
        )
    )