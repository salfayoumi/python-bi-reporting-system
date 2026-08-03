"""
data_validator.py
Validates the customer and order datasets before analysis.
"""

from pathlib import Path

import pandas as pd


VALID_REGIONS = {
    "Istanbul",
    "Ankara",
    "Izmir",
    "Bursa",
    "Antalya",
}

VALID_SEGMENTS = {
    "Enterprise",
    "SMB",
    "Startup",
}

VALID_PRODUCTS = {
    "CRM Basic",
    "CRM Pro",
    "CRM Enterprise",
    "Support Pack",
    "Training",
}

VALID_STATUSES = {
    "Won",
    "Lost",
    "Churned",
}


def load_data(
    customers_path: str | Path = "data/customers.csv",
    orders_path: str | Path = "data/orders.csv",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the customer and order CSV files.

    Returns:
        A tuple containing the customers and orders DataFrames.
    """
    customers_path = Path(customers_path)
    orders_path = Path(orders_path)

    if not customers_path.exists():
        raise FileNotFoundError(
            f"Customer file was not found: {customers_path}"
        )

    if not orders_path.exists():
        raise FileNotFoundError(
            f"Order file was not found: {orders_path}"
        )

    customers = pd.read_csv(customers_path)
    orders = pd.read_csv(orders_path)

    return customers, orders


def add_result(
    results: list[dict],
    check_name: str,
    passed: bool,
    details: str,
) -> None:
    """Add one validation result to the results list."""
    results.append(
        {
            "check": check_name,
            "passed": passed,
            "details": details,
        }
    )


def validate_data(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run integrity and quality checks on the CRM datasets.

    Returns:
        A DataFrame containing the result of every validation check.
    """
    results: list[dict] = []

    # Work on copies so the original DataFrames are not modified.
    customers = customers.copy()
    orders = orders.copy()

    # ------------------------------------------------------------------
    # 1. Missing-value checks
    # ------------------------------------------------------------------
    customer_missing = int(customers.isna().sum().sum())
    order_missing = int(orders.isna().sum().sum())

    add_result(
        results,
        "Customer missing values",
        customer_missing == 0,
        f"{customer_missing} missing value(s) found.",
    )

    add_result(
        results,
        "Order missing values",
        order_missing == 0,
        f"{order_missing} missing value(s) found.",
    )

    # ------------------------------------------------------------------
    # 2. Duplicate-row checks
    # ------------------------------------------------------------------
    duplicate_customers = int(customers.duplicated().sum())
    duplicate_orders = int(orders.duplicated().sum())

    add_result(
        results,
        "Duplicate customer rows",
        duplicate_customers == 0,
        f"{duplicate_customers} duplicate row(s) found.",
    )

    add_result(
        results,
        "Duplicate order rows",
        duplicate_orders == 0,
        f"{duplicate_orders} duplicate row(s) found.",
    )

    # ------------------------------------------------------------------
    # 3. Unique-ID checks
    # ------------------------------------------------------------------
    duplicate_customer_ids = int(
        customers["customer_id"].duplicated().sum()
    )
    duplicate_order_ids = int(
        orders["order_id"].duplicated().sum()
    )

    add_result(
        results,
        "Unique customer IDs",
        duplicate_customer_ids == 0,
        f"{duplicate_customer_ids} duplicate customer ID(s) found.",
    )

    add_result(
        results,
        "Unique order IDs",
        duplicate_order_ids == 0,
        f"{duplicate_order_ids} duplicate order ID(s) found.",
    )

    # ------------------------------------------------------------------
    # 4. Foreign-key check
    # ------------------------------------------------------------------
    valid_customer_ids = set(customers["customer_id"])

    orphan_orders = orders[
        ~orders["customer_id"].isin(valid_customer_ids)
    ]

    add_result(
        results,
        "Valid order customer references",
        orphan_orders.empty,
        f"{len(orphan_orders)} orphan order(s) found.",
    )

    # ------------------------------------------------------------------
    # 5. Allowed-category checks
    # ------------------------------------------------------------------
    invalid_customer_regions = customers[
        ~customers["region"].isin(VALID_REGIONS)
    ]

    invalid_order_regions = orders[
        ~orders["region"].isin(VALID_REGIONS)
    ]

    invalid_customer_segments = customers[
        ~customers["segment"].isin(VALID_SEGMENTS)
    ]

    invalid_order_segments = orders[
        ~orders["segment"].isin(VALID_SEGMENTS)
    ]

    invalid_products = orders[
        ~orders["product"].isin(VALID_PRODUCTS)
    ]

    invalid_statuses = orders[
        ~orders["status"].isin(VALID_STATUSES)
    ]

    add_result(
        results,
        "Valid customer regions",
        invalid_customer_regions.empty,
        f"{len(invalid_customer_regions)} invalid value(s) found.",
    )

    add_result(
        results,
        "Valid order regions",
        invalid_order_regions.empty,
        f"{len(invalid_order_regions)} invalid value(s) found.",
    )

    add_result(
        results,
        "Valid customer segments",
        invalid_customer_segments.empty,
        f"{len(invalid_customer_segments)} invalid value(s) found.",
    )

    add_result(
        results,
        "Valid order segments",
        invalid_order_segments.empty,
        f"{len(invalid_order_segments)} invalid value(s) found.",
    )

    add_result(
        results,
        "Valid products",
        invalid_products.empty,
        f"{len(invalid_products)} invalid value(s) found.",
    )

    add_result(
        results,
        "Valid order statuses",
        invalid_statuses.empty,
        f"{len(invalid_statuses)} invalid value(s) found.",
    )

    # ------------------------------------------------------------------
    # 6. Numeric-value checks
    # ------------------------------------------------------------------
    invalid_quantities = orders[
        (orders["quantity"] < 1) | (orders["quantity"] > 5)
    ]

    non_positive_prices = orders[
        orders["unit_price"] <= 0
    ]

    non_positive_totals = orders[
        orders["total_amount"] <= 0
    ]

    add_result(
        results,
        "Valid order quantities",
        invalid_quantities.empty,
        f"{len(invalid_quantities)} invalid quantity value(s) found.",
    )

    add_result(
        results,
        "Positive unit prices",
        non_positive_prices.empty,
        f"{len(non_positive_prices)} invalid price value(s) found.",
    )

    add_result(
        results,
        "Positive total amounts",
        non_positive_totals.empty,
        f"{len(non_positive_totals)} invalid total value(s) found.",
    )

    # ------------------------------------------------------------------
    # 7. Order-total calculation check
    # ------------------------------------------------------------------
    expected_totals = (
        orders["quantity"] * orders["unit_price"]
    ).round(2)

    incorrect_totals = orders[
        expected_totals != orders["total_amount"].round(2)
    ]

    add_result(
        results,
        "Correct order totals",
        incorrect_totals.empty,
        f"{len(incorrect_totals)} incorrect total(s) found.",
    )

    # ------------------------------------------------------------------
    # 8. Date validation
    # ------------------------------------------------------------------
    customers["since_parsed"] = pd.to_datetime(
        customers["since"],
        errors="coerce",
    )

    orders["order_date_parsed"] = pd.to_datetime(
        orders["order_date"],
        errors="coerce",
    )

    invalid_customer_dates = int(
        customers["since_parsed"].isna().sum()
    )

    invalid_order_dates = int(
        orders["order_date_parsed"].isna().sum()
    )

    add_result(
        results,
        "Valid customer dates",
        invalid_customer_dates == 0,
        f"{invalid_customer_dates} invalid date(s) found.",
    )

    add_result(
        results,
        "Valid order dates",
        invalid_order_dates == 0,
        f"{invalid_order_dates} invalid date(s) found.",
    )

    # ------------------------------------------------------------------
    # 9. Month, quarter, and year consistency
    # ------------------------------------------------------------------
    valid_order_date_rows = orders["order_date_parsed"].notna()

    expected_month = orders.loc[
        valid_order_date_rows,
        "order_date_parsed",
    ].dt.strftime("%Y-%m")

    valid_dates = orders.loc[
        valid_order_date_rows,
        "order_date_parsed",
    ]

    expected_quarter = (
        valid_dates.dt.year.astype(str)
        + "-Q"
        + valid_dates.dt.quarter.astype(str)
    )    

    expected_year = orders.loc[
        valid_order_date_rows,
        "order_date_parsed",
    ].dt.year

    incorrect_months = (
        orders.loc[valid_order_date_rows, "month"].astype(str)
        != expected_month
    ).sum()

    incorrect_quarters = (
        orders.loc[valid_order_date_rows, "quarter"].astype(str)
        != expected_quarter
    ).sum()

    incorrect_years = (
        orders.loc[valid_order_date_rows, "year"]
        != expected_year
    ).sum()

    add_result(
        results,
        "Correct month values",
        incorrect_months == 0,
        f"{incorrect_months} inconsistent month value(s) found.",
    )

    add_result(
        results,
        "Correct quarter values",
        incorrect_quarters == 0,
        f"{incorrect_quarters} inconsistent quarter value(s) found.",
    )

    add_result(
        results,
        "Correct year values",
        incorrect_years == 0,
        f"{incorrect_years} inconsistent year value(s) found.",
    )

    # ------------------------------------------------------------------
    # 10. Customer/order consistency
    # ------------------------------------------------------------------
    customer_details = customers[
        [
            "customer_id",
            "region",
            "segment",
            "account_manager",
            "since_parsed",
        ]
    ].rename(
        columns={
            "region": "customer_region",
            "segment": "customer_segment",
            "account_manager": "customer_account_manager",
        }
    )

    merged = orders.merge(
        customer_details,
        on="customer_id",
        how="left",
    )

    inconsistent_regions = merged[
        merged["region"] != merged["customer_region"]
    ]

    inconsistent_segments = merged[
        merged["segment"] != merged["customer_segment"]
    ]

    inconsistent_managers = merged[
        merged["account_manager"]
        != merged["customer_account_manager"]
    ]

    add_result(
        results,
        "Consistent customer regions",
        inconsistent_regions.empty,
        f"{len(inconsistent_regions)} inconsistency/inconsistencies found.",
    )

    add_result(
        results,
        "Consistent customer segments",
        inconsistent_segments.empty,
        f"{len(inconsistent_segments)} inconsistency/inconsistencies found.",
    )

    add_result(
        results,
        "Consistent account managers",
        inconsistent_managers.empty,
        f"{len(inconsistent_managers)} inconsistency/inconsistencies found.",
    )

    # ------------------------------------------------------------------
    # 11. Orders before customer registration
    # ------------------------------------------------------------------
    orders_before_registration = merged[
        merged["order_date_parsed"] < merged["since_parsed"]
    ]

    add_result(
        results,
        "Orders after customer registration",
        orders_before_registration.empty,
        (
            f"{len(orders_before_registration)} order(s) occurred "
            "before the customer's registration date."
        ),
    )

    return pd.DataFrame(results)


def print_validation_report(results: pd.DataFrame) -> None:
    """Print the validation results in a readable terminal format."""
    print("\n" + "=" * 70)
    print("CRM DATA VALIDATION REPORT")
    print("=" * 70)

    for _, result in results.iterrows():
        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"[{status}] {result['check']}: "
            f"{result['details']}"
        )

    passed_checks = int(results["passed"].sum())
    total_checks = len(results)
    failed_checks = total_checks - passed_checks

    print("-" * 70)
    print(f"Passed checks: {passed_checks}/{total_checks}")
    print(f"Failed checks: {failed_checks}/{total_checks}")
    print("=" * 70)


def main() -> None:
    """Load the datasets, validate them, and print the report."""
    try:
        customers, orders = load_data()
        results = validate_data(customers, orders)
        print_validation_report(results)

    except (FileNotFoundError, KeyError, pd.errors.ParserError) as error:
        print(f"Validation could not be completed: {error}")


if __name__ == "__main__":
    main()