"""
modules/kpi_engine.py

Loads CRM datasets and calculates the core business KPIs used by
the dashboard, decision-support engine, visualizations, and exports.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from modules.domain import (
    KPIBundle,
    MomGrowthStatus,
    TrendDirection,
    classify_trend,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ORDERS_PATH = PROJECT_ROOT / "data" / "orders.csv"
DEFAULT_CUSTOMERS_PATH = PROJECT_ROOT / "data" / "customers.csv"

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
    "year",
    "status",
    "product",
    "region",
    "account_manager",
    "quantity",
    "unit_price",
    "total_amount",
    "segment",
}

REQUIRED_CUSTOMER_COLUMNS = {
    "customer_id",
    "since",
    "segment",
    "region",
}



def load_data(
    *,
    orders_path: str | Path = DEFAULT_ORDERS_PATH,
    customers_path: str | Path = DEFAULT_CUSTOMERS_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the order and customer datasets.

    Dates are parsed automatically so downstream modules can use
    datetime operations without additional conversion.
    """

    orders_path = Path(orders_path)
    customers_path = Path(customers_path)

    missing_paths = [
        str(path)
        for path in (orders_path, customers_path)
        if not path.is_file()
    ]

    if missing_paths:
        raise ValueError(
            "Required data file(s) could not be found: "
            + ", ".join(missing_paths)
        )

    try:
        orders = pd.read_csv(
            orders_path,
            parse_dates=["order_date"],
        )

        customers = pd.read_csv(
            customers_path,
            parse_dates=["since"],
        )
    except (OSError, pd.errors.ParserError) as error:
        raise ValueError(
            "The CRM data files could not be loaded. "
            "Check that the CSV files exist and are valid."
        ) from error

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

    Filters use AND logic. Region and segment restrict both datasets.
    Year and product restrict orders only. The returned customer DataFrame
    therefore represents the customer population in scope, while active
    customers are derived explicitly from matching orders.
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

    if filtered_customers.empty:
        raise ValueError(
            "The selected filters produced orders but no customer "
            "population for the selected customer-level scope."
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
    *,
    orders: pd.DataFrame,
    customers: pd.DataFrame,
) -> dict:
    """
    Validate CRM data and return a structured report without producing I/O.

    Structural problems raise ValueError. Data-quality and referential-
    integrity findings are returned as measurable report fields so callers
    can choose how to present or log them.
    """

    if orders.empty:
        raise ValueError("The orders dataset is empty.")

    if customers.empty:
        raise ValueError("The customers dataset is empty.")

    missing_order_columns = _missing_required_columns(
        orders,
        REQUIRED_ORDER_COLUMNS,
    )
    missing_customer_columns = _missing_required_columns(
        customers,
        REQUIRED_CUSTOMER_COLUMNS,
    )

    if missing_order_columns:
        raise ValueError(
            "Orders dataset is missing required columns: "
            + ", ".join(missing_order_columns)
        )

    if missing_customer_columns:
        raise ValueError(
            "Customers dataset is missing required columns: "
            + ", ".join(missing_customer_columns)
        )

    order_missing_values = int(orders.isna().sum().sum())
    customer_missing_values = int(customers.isna().sum().sum())

    order_duplicate_rows = int(orders.duplicated().sum())
    customer_duplicate_rows = int(customers.duplicated().sum())

    duplicate_order_ids = int(
        orders["order_id"].duplicated(keep=False).sum()
    )
    duplicate_customer_ids = int(
        customers["customer_id"].duplicated(keep=False).sum()
    )

    numeric_total = pd.to_numeric(
        orders["total_amount"],
        errors="coerce",
    )
    numeric_quantity = pd.to_numeric(
        orders["quantity"],
        errors="coerce",
    )
    numeric_unit_price = pd.to_numeric(
        orders["unit_price"],
        errors="coerce",
    )

    negative_revenue = int((numeric_total < 0).sum())
    invalid_quantity = int((numeric_quantity <= 0).sum())
    invalid_unit_price = int((numeric_unit_price <= 0).sum())

    expected_total = (
        numeric_quantity
        * numeric_unit_price
    ).round(2)

    total_amount_mismatch = int(
        (
            expected_total.notna()
            & numeric_total.notna()
            & (
                expected_total
                != numeric_total.round(2)
            )
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
        .isin(unknown_statuses)
        .sum()
    )

    parsed_order_dates = pd.to_datetime(
        orders["order_date"],
        errors="coerce",
    )
    parsed_customer_dates = pd.to_datetime(
        customers["since"],
        errors="coerce",
    )

    invalid_order_dates = int(
        parsed_order_dates.isna().sum()
    )
    invalid_customer_dates = int(
        parsed_customer_dates.isna().sum()
    )

    valid_order_dates = parsed_order_dates.notna()

    expected_month = (
        parsed_order_dates.loc[valid_order_dates]
        .dt.strftime("%Y-%m")
    )
    expected_quarter = (
        parsed_order_dates.loc[valid_order_dates]
        .dt.year.astype(str)
        + "-Q"
        + parsed_order_dates.loc[valid_order_dates]
        .dt.quarter.astype(str)
    )
    expected_year = (
        parsed_order_dates.loc[valid_order_dates]
        .dt.year
    )

    month_mismatch = int(
        (
            orders.loc[valid_order_dates, "month"].astype(str)
            != expected_month
        ).sum()
    )
    quarter_mismatch = int(
        (
            orders.loc[valid_order_dates, "quarter"].astype(str)
            != expected_quarter
        ).sum()
    )

    stored_year = pd.to_numeric(
        orders.loc[valid_order_dates, "year"],
        errors="coerce",
    )
    year_mismatch = int(
        (
            stored_year
            != expected_year
        ).sum()
    )

    customer_ids = set(
        customers["customer_id"]
        .dropna()
    )
    orphan_order_count = int(
        (
            ~orders["customer_id"].isin(customer_ids)
        ).sum()
    )

    customer_reference = customers[
        ["customer_id", "since", "region", "segment"]
    ].copy()
    customer_reference["since"] = pd.to_datetime(
        customer_reference["since"],
        errors="coerce",
    )

    merged = orders[
        ["customer_id", "order_date", "region", "segment"]
    ].copy().merge(
        customer_reference,
        on="customer_id",
        how="left",
        suffixes=("_order", "_customer"),
    )

    merged["order_date"] = pd.to_datetime(
        merged["order_date"],
        errors="coerce",
    )

    comparable_dates = (
        merged["order_date"].notna()
        & merged["since"].notna()
    )
    orders_before_registration = int(
        (
            merged.loc[comparable_dates, "order_date"]
            < merged.loc[comparable_dates, "since"]
        ).sum()
    )

    comparable_customer_rows = merged["since"].notna()
    region_mismatch = int(
        (
            merged.loc[
                comparable_customer_rows,
                "region_order",
            ].astype(str)
            != merged.loc[
                comparable_customer_rows,
                "region_customer",
            ].astype(str)
        ).sum()
    )
    segment_mismatch = int(
        (
            merged.loc[
                comparable_customer_rows,
                "segment_order",
            ].astype(str)
            != merged.loc[
                comparable_customer_rows,
                "segment_customer",
            ].astype(str)
        ).sum()
    )

    report = {
        "customers": {
            "rows": len(customers),
            "columns": len(customers.columns),
            "missing_values": customer_missing_values,
            "duplicate_rows": customer_duplicate_rows,
            "duplicate_customer_ids": duplicate_customer_ids,
            "invalid_dates": invalid_customer_dates,
        },
        "orders": {
            "rows": len(orders),
            "columns": len(orders.columns),
            "missing_values": order_missing_values,
            "duplicate_rows": order_duplicate_rows,
            "duplicate_order_ids": duplicate_order_ids,
            "negative_revenue": negative_revenue,
            "invalid_quantity": invalid_quantity,
            "invalid_unit_price": invalid_unit_price,
            "total_amount_mismatch": total_amount_mismatch,
            "unknown_status_count": unknown_status_count,
            "unknown_statuses": unknown_statuses,
            "invalid_dates": invalid_order_dates,
            "month_mismatch": month_mismatch,
            "quarter_mismatch": quarter_mismatch,
            "year_mismatch": year_mismatch,
            "orphan_customer_references": orphan_order_count,
            "orders_before_customer_registration": (
                orders_before_registration
            ),
            "customer_region_mismatch": region_mismatch,
            "customer_segment_mismatch": segment_mismatch,
        },
    }

    issue_fields = [
        customer_missing_values,
        customer_duplicate_rows,
        duplicate_customer_ids,
        invalid_customer_dates,
        order_missing_values,
        order_duplicate_rows,
        duplicate_order_ids,
        negative_revenue,
        invalid_quantity,
        invalid_unit_price,
        total_amount_mismatch,
        unknown_status_count,
        invalid_order_dates,
        month_mismatch,
        quarter_mismatch,
        year_mismatch,
        orphan_order_count,
        orders_before_registration,
        region_mismatch,
        segment_mismatch,
    ]

    report["passed"] = sum(issue_fields) == 0

    return report


def print_validation_report(
    report: dict,
) -> None:
    """Print a previously calculated validation report."""

    customers = report["customers"]
    orders = report["orders"]

    print("\n" + "=" * 55)
    print("  DATA VALIDATION REPORT")
    print("=" * 55)

    print("\nCustomers Dataset")
    print("-" * 55)
    print(f"   Rows              : {customers['rows']:,}")
    print(f"   Columns           : {customers['columns']}")
    print(f"   Missing Values    : {customers['missing_values']}")
    print(f"   Duplicate Rows    : {customers['duplicate_rows']}")
    print(f"   Duplicate IDs     : {customers['duplicate_customer_ids']}")
    print(f"   Invalid Dates     : {customers['invalid_dates']}")

    print("\nOrders Dataset")
    print("-" * 55)
    print(f"   Rows              : {orders['rows']:,}")
    print(f"   Columns           : {orders['columns']}")
    print(f"   Missing Values    : {orders['missing_values']}")
    print(f"   Duplicate Rows    : {orders['duplicate_rows']}")
    print(f"   Duplicate IDs     : {orders['duplicate_order_ids']}")
    print(f"   Negative Revenue  : {orders['negative_revenue']}")
    print(f"   Invalid Quantity  : {orders['invalid_quantity']}")
    print(f"   Invalid Unit Price: {orders['invalid_unit_price']}")
    print(f"   Amount Mismatches : {orders['total_amount_mismatch']}")
    print(f"   Unknown Status    : {orders['unknown_status_count']}")
    print(f"   Invalid Dates     : {orders['invalid_dates']}")
    print(f"   Month Mismatches  : {orders['month_mismatch']}")
    print(f"   Quarter Mismatches: {orders['quarter_mismatch']}")
    print(f"   Year Mismatches   : {orders['year_mismatch']}")
    print(f"   Orphan Customers  : {orders['orphan_customer_references']}")
    print(
        "   Pre-registration : "
        f"{orders['orders_before_customer_registration']}"
    )
    print(f"   Region Mismatches : {orders['customer_region_mismatch']}")
    print(f"   Segment Mismatches: {orders['customer_segment_mismatch']}")

    if orders["unknown_statuses"]:
        print(
            "   Unknown Values    : "
            + ", ".join(orders["unknown_statuses"])
        )

    print()
    if report["passed"]:
        print("✓ Dataset validation completed successfully.")
    else:
        print("⚠ Dataset validation completed with warnings.")
    print("=" * 55)


def _won_orders(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Return only successfully won orders."""

    return orders[
        orders["status"] == STATUS_WON
    ]


def _complete_monthly_revenue(
    orders: pd.DataFrame,
) -> pd.Series:
    """
    Return won-order revenue for every calendar month in the data range.

    Months without won revenue are retained with a value of zero so
    month-over-month, trend, and forecasting calculations preserve the
    real calendar spacing.
    """

    order_dates = pd.to_datetime(
        orders["order_date"],
        errors="coerce",
    ).dropna()

    if order_dates.empty:
        return pd.Series(
            dtype=float,
            name="revenue",
        )

    first_period = order_dates.min().to_period("M")
    last_period = order_dates.max().to_period("M")

    complete_periods = pd.period_range(
        start=first_period,
        end=last_period,
        freq="M",
    )

    won_orders = _won_orders(orders).copy()

    if won_orders.empty:
        return pd.Series(
            0.0,
            index=complete_periods,
            name="revenue",
            dtype=float,
        )

    won_orders["_revenue_period"] = (
        pd.to_datetime(
            won_orders["order_date"],
            errors="coerce",
        ).dt.to_period("M")
    )

    monthly_revenue = (
        won_orders.groupby("_revenue_period")[
            "total_amount"
        ]
        .sum()
        .reindex(
            complete_periods,
            fill_value=0.0,
        )
        .astype(float)
    )

    monthly_revenue.name = "revenue"

    return monthly_revenue


# ── 1. Revenue KPIs ───────────────────────────────────────────────────────────
def revenue_kpis(
    orders: pd.DataFrame,
) -> dict:
    """Calculate revenue-related KPIs using won orders."""

    won_orders = _won_orders(orders)

    total_revenue = float(
        won_orders["total_amount"].sum()
    )

    avg_order_value = (
        float(
            won_orders["total_amount"].mean()
        )
        if not won_orders.empty
        else 0.0
    )

    monthly_revenue = _complete_monthly_revenue(
        orders
    )

    current_month = None
    previous_month = None
    current_month_revenue = 0.0
    previous_month_revenue = None
    mom_growth = None
    mom_growth_status = MomGrowthStatus.UNAVAILABLE.value

    if not monthly_revenue.empty:
        current_month = str(
            monthly_revenue.index[-1]
        )
        current_month_revenue = float(
            monthly_revenue.iloc[-1]
        )

    if len(monthly_revenue) >= 2:
        previous_month = str(
            monthly_revenue.index[-2]
        )
        previous_month_revenue = float(
            monthly_revenue.iloc[-2]
        )

        if previous_month_revenue == 0:
            if current_month_revenue == 0:
                mom_growth = 0.0
                mom_growth_status = MomGrowthStatus.STABLE.value
            else:
                mom_growth_status = MomGrowthStatus.FROM_ZERO.value
        else:
            mom_growth = (
                (
                    current_month_revenue
                    - previous_month_revenue
                )
                / previous_month_revenue
                * 100
            )

            if mom_growth > 0:
                mom_growth_status = MomGrowthStatus.GROWTH.value
            elif mom_growth < 0:
                mom_growth_status = MomGrowthStatus.DECLINE.value
            else:
                mom_growth_status = MomGrowthStatus.STABLE.value

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
        "previous_month_revenue": (
            round(
                previous_month_revenue,
                2,
            )
            if previous_month_revenue is not None
            else None
        ),
        "mom_growth_pct": (
            round(
                mom_growth,
                2,
            )
            if mom_growth is not None
            else None
        ),
        "mom_growth_status": (
            mom_growth_status
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
        "churned_order_rate_pct": round(
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

    complete_monthly_revenue = (
        _complete_monthly_revenue(
            orders
        )
    )

    monthly_revenue = (
        complete_monthly_revenue
        .rename_axis("month")
        .reset_index(name="revenue")
    )

    monthly_revenue["month"] = (
        monthly_revenue["month"]
        .astype(str)
    )

    monthly_revenue["revenue"] = (
        monthly_revenue["revenue"]
        .round(2)
    )

    won_orders = _won_orders(orders)

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
        len(monthly_revenue),
        dtype=float,
    )

    if len(x_values) > 1:
        slope = float(
            np.polyfit(
                x_values,
                monthly_revenue["revenue"],
                1,
            )[0]
        )
    else:
        slope = 0.0

    average_monthly_revenue = (
        float(
            monthly_revenue["revenue"].mean()
        )
        if not monthly_revenue.empty
        else 0.0
    )

    trend_state = classify_trend(
        slope,
        average_monthly_revenue,
    )
    trend_direction_code = trend_state.value

    trend_direction = {
        TrendDirection.GROWING: "↑ Growing",
        TrendDirection.DECLINING: "↓ Declining",
        TrendDirection.STABLE: "→ Stable",
    }[trend_state]

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
        "trend_direction_code": (
            trend_direction_code
        ),
        "trend_direction": (
            trend_direction
        ),
    }


# ── Master Runner ─────────────────────────────────────────────────────────────
@dataclass
class AnalysisResult:
    """Typed boundary between calculation results and filtered source data."""

    kpis: KPIBundle
    orders: pd.DataFrame
    customers: pd.DataFrame


def compute_analysis(
    orders: pd.DataFrame | None = None,
    customers: pd.DataFrame | None = None,
    *,
    orders_path: str | Path = DEFAULT_ORDERS_PATH,
    customers_path: str | Path = DEFAULT_CUSTOMERS_PATH,
    region: str | None = None,
    year: int | None = None,
    segment: str | None = None,
    product: str | None = None,
    print_validation: bool = True,
) -> AnalysisResult:
    """Run filtering, validation, and KPI calculation as one analysis."""

    if orders is None and customers is None:
        resolved_orders, resolved_customers = load_data(
            orders_path=orders_path,
            customers_path=customers_path,
        )
    elif orders is None or customers is None:
        raise ValueError(
            "orders and customers must either both be provided "
            "or both be omitted."
        )
    else:
        resolved_orders = orders.copy()
        resolved_customers = customers.copy()

    source_validation_report = validate_data(
        orders=resolved_orders,
        customers=resolved_customers,
    )

    (
        filtered_orders,
        scoped_customers,
        applied_filters,
    ) = apply_filters(
        resolved_orders,
        resolved_customers,
        region=region,
        year=year,
        segment=segment,
        product=product,
    )

    validation_report = validate_data(
        orders=filtered_orders,
        customers=scoped_customers,
    )

    if print_validation:
        print_validation_report(validation_report)

    active_customer_count = int(
        filtered_orders["customer_id"].nunique()
    )

    minimum_date = filtered_orders["order_date"].min().date()
    maximum_date = filtered_orders["order_date"].max().date()

    kpis: KPIBundle = {
        "revenue": revenue_kpis(filtered_orders),
        "sales": sales_kpis(filtered_orders),
        "products": product_kpis(filtered_orders),
        "regions": regional_kpis(filtered_orders),
        "trends": trend_analysis(filtered_orders),
        "validation": validation_report,
        "source_validation": source_validation_report,
        "filters": applied_filters,
        "meta": {
            "total_customers": len(scoped_customers),
            "active_customers": active_customer_count,
            "total_orders": len(filtered_orders),
            "date_range": f"{minimum_date} → {maximum_date}",
            "generated_at": pd.Timestamp.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        },
    }

    return AnalysisResult(
        kpis=kpis,
        orders=filtered_orders.reset_index(drop=True),
        customers=scoped_customers.reset_index(drop=True),
    )


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
) -> KPIBundle:
    """
    Backward-compatible KPI-only API.

    Use compute_analysis() when filtered DataFrames are also required.
    """

    return compute_analysis(
        orders,
        customers,
        orders_path=orders_path,
        customers_path=customers_path,
        region=region,
        year=year,
        segment=segment,
        product=product,
        print_validation=print_validation_report,
    ).kpis


if __name__ == "__main__":
    kpis = compute_all_kpis()

    print(
        json.dumps(
            kpis,
            indent=2,
            default=str,
        )
    )