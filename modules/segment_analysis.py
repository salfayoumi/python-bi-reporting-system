"""
modules/segment_analysis.py

Calculates customer-segment performance metrics from the CRM
customers and orders datasets.
"""

from pathlib import Path

import pandas as pd


DEFAULT_ORDERS_PATH = Path("data/orders.csv")
DEFAULT_CUSTOMERS_PATH = Path("data/customers.csv")

STATUS_WON = "Won"
STATUS_LOST = "Lost"
STATUS_CHURNED = "Churned"


def load_segment_data(
    orders_path: str | Path = DEFAULT_ORDERS_PATH,
    customers_path: str | Path = DEFAULT_CUSTOMERS_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the order and customer datasets."""

    orders = pd.read_csv(
        orders_path,
        parse_dates=["order_date"],
    )

    customers = pd.read_csv(
        customers_path,
        parse_dates=["since"],
    )

    return orders, customers


def _filter_orders_by_status(
    orders: pd.DataFrame,
    status: str,
) -> pd.DataFrame:
    """Return orders matching the requested status."""

    return orders[
        orders["status"] == status
    ]


def _calculate_percentage(
    numerator: float,
    denominator: float,
) -> float:
    """Calculate a percentage safely."""

    if denominator == 0:
        return 0.0

    return (
        numerator
        / denominator
        * 100
    )


def calculate_segment_performance(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
) -> dict:
    """
    Calculate business-performance metrics for each customer segment.

    Metrics include:
        - registered and active customers
        - total, won, lost, and churned orders
        - total revenue
        - revenue share
        - revenue per customer
        - average order value
        - win rate
        - churn rate
        - top product
    """

    segment_results = {}

    segments = sorted(
        set(
            customers["segment"]
            .dropna()
        )
        | set(
            orders["segment"]
            .dropna()
        )
    )

    company_won_orders = (
        _filter_orders_by_status(
            orders,
            STATUS_WON,
        )
    )

    company_total_revenue = (
        company_won_orders[
            "total_amount"
        ].sum()
    )

    for segment in segments:
        segment_customers = customers[
            customers["segment"] == segment
        ]

        segment_orders = orders[
            orders["segment"] == segment
        ]

        segment_won_orders = (
            _filter_orders_by_status(
                segment_orders,
                STATUS_WON,
            )
        )

        segment_lost_orders = (
            _filter_orders_by_status(
                segment_orders,
                STATUS_LOST,
            )
        )

        segment_churned_orders = (
            _filter_orders_by_status(
                segment_orders,
                STATUS_CHURNED,
            )
        )

        customer_count = len(
            segment_customers
        )

        active_customer_count = (
            segment_orders[
                "customer_id"
            ].nunique()
        )

        total_order_count = len(
            segment_orders
        )

        won_order_count = len(
            segment_won_orders
        )

        lost_order_count = len(
            segment_lost_orders
        )

        churned_order_count = len(
            segment_churned_orders
        )

        total_revenue = (
            segment_won_orders[
                "total_amount"
            ].sum()
        )

        average_order_value = (
            segment_won_orders[
                "total_amount"
            ].mean()
            if not segment_won_orders.empty
            else 0.0
        )

        closed_opportunities = (
            won_order_count
            + lost_order_count
        )

        win_rate = _calculate_percentage(
            won_order_count,
            closed_opportunities,
        )

        churn_rate = _calculate_percentage(
            churned_order_count,
            total_order_count,
        )

        revenue_share = _calculate_percentage(
            total_revenue,
            company_total_revenue,
        )

        revenue_per_customer = (
            total_revenue
            / customer_count
            if customer_count
            else 0.0
        )

        product_revenue = (
            segment_won_orders
            .groupby("product")[
                "total_amount"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        top_product = (
            product_revenue.index[0]
            if not product_revenue.empty
            else "N/A"
        )

        segment_results[segment] = {
            "customer_count": customer_count,
            "active_customers": (
                active_customer_count
            ),
            "total_orders": total_order_count,
            "won_orders": won_order_count,
            "lost_orders": lost_order_count,
            "churned_orders": (
                churned_order_count
            ),
            "total_revenue": round(
                total_revenue,
                2,
            ),
            "revenue_share_pct": round(
                revenue_share,
                2,
            ),
            "revenue_per_customer": round(
                revenue_per_customer,
                2,
            ),
            "avg_order_value": round(
                average_order_value,
                2,
            ),
            "win_rate_pct": round(
                win_rate,
                2,
            ),
            "churn_rate_pct": round(
                churn_rate,
                2,
            ),
            "top_product": top_product,
        }

    return segment_results


def summarize_segment_performance(
    segment_results: dict,
) -> dict:
    """Identify the leading segment for key business metrics."""

    if not segment_results:
        return {
            "highest_revenue_segment": "N/A",
            "highest_revenue_per_customer_segment": "N/A",
            "highest_win_rate_segment": "N/A",
            "lowest_churn_rate_segment": "N/A",
        }

    highest_revenue_segment = max(
        segment_results,
        key=lambda segment: (
            segment_results[
                segment
            ][
                "total_revenue"
            ]
        ),
    )

    highest_revenue_per_customer_segment = max(
        segment_results,
        key=lambda segment: (
            segment_results[
                segment
            ][
                "revenue_per_customer"
            ]
        ),
    )

    highest_win_rate_segment = max(
        segment_results,
        key=lambda segment: (
            segment_results[
                segment
            ][
                "win_rate_pct"
            ]
        ),
    )

    lowest_churn_rate_segment = min(
        segment_results,
        key=lambda segment: (
            segment_results[
                segment
            ][
                "churn_rate_pct"
            ]
        ),
    )

    return {
        "highest_revenue_segment": (
            highest_revenue_segment
        ),
        "highest_revenue_per_customer_segment": (
            highest_revenue_per_customer_segment
        ),
        "highest_win_rate_segment": (
            highest_win_rate_segment
        ),
        "lowest_churn_rate_segment": (
            lowest_churn_rate_segment
        ),
    }


def compute_segment_analysis(
    orders_path: str | Path = DEFAULT_ORDERS_PATH,
    customers_path: str | Path = DEFAULT_CUSTOMERS_PATH,
) -> dict:
    """Load the datasets and run the complete segment analysis."""

    orders, customers = load_segment_data(
        orders_path,
        customers_path,
    )

    performance = (
        calculate_segment_performance(
            orders,
            customers,
        )
    )

    summary = (
        summarize_segment_performance(
            performance
        )
    )

    return {
        "performance": performance,
        "summary": summary,
    }