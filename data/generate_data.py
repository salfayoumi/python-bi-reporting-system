"""
data/generate_data.py

Generate a deterministic but behaviorally varied synthetic CRM dataset.

Run:
    python data/generate_data.py
"""

from datetime import datetime, timedelta
from pathlib import Path
import random

import numpy as np
import pandas as pd


RANDOM_SEED = 42

N_CUSTOMERS = 200
N_ORDERS = 1500
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

REGIONS = [
    "Istanbul",
    "Ankara",
    "Izmir",
    "Bursa",
    "Antalya",
]
SEGMENTS = [
    "Enterprise",
    "SMB",
    "Startup",
]
PRODUCTS = {
    "CRM Basic": (299, 599),
    "CRM Pro": (799, 1499),
    "CRM Enterprise": (2000, 4999),
    "Support Pack": (150, 400),
    "Training": (200, 600),
}
STATUSES = (
    "Won",
    "Lost",
    "Churned",
)

BASE_STATUS_WEIGHTS = {
    "Enterprise": {
        "Won": 0.72,
        "Lost": 0.18,
        "Churned": 0.10,
    },
    "SMB": {
        "Won": 0.64,
        "Lost": 0.22,
        "Churned": 0.14,
    },
    "Startup": {
        "Won": 0.55,
        "Lost": 0.27,
        "Churned": 0.18,
    },
}

PRODUCT_STATUS_ADJUSTMENTS = {
    "CRM Basic": {
        "Won": -0.01,
        "Lost": -0.01,
        "Churned": 0.02,
    },
    "CRM Pro": {
        "Won": 0.01,
        "Lost": 0.00,
        "Churned": -0.01,
    },
    "CRM Enterprise": {
        "Won": 0.03,
        "Lost": -0.02,
        "Churned": -0.01,
    },
    "Support Pack": {
        "Won": 0.00,
        "Lost": 0.01,
        "Churned": -0.01,
    },
    "Training": {
        "Won": 0.05,
        "Lost": -0.03,
        "Churned": -0.02,
    },
}


def random_date(
    start: datetime,
    end: datetime,
) -> datetime:
    """Return a random date within an inclusive datetime range."""

    return start + timedelta(
        days=random.randint(
            0,
            (end - start).days,
        )
    )


def status_probabilities(
    segment: str,
    product: str,
    order_date: datetime,
    account_manager: str,
) -> dict[str, float]:
    """
    Return context-sensitive synthetic order-status probabilities.

    Probabilities vary by segment, product, simulated year, and account
    manager so the demo does not bake a near-constant churned-order rate
    or win rate into every analytical slice.
    """

    weights = BASE_STATUS_WEIGHTS[
        segment
    ].copy()

    for status, adjustment in (
        PRODUCT_STATUS_ADJUSTMENTS[
            product
        ].items()
    ):
        weights[status] += adjustment

    if order_date.year >= 2024:
        weights["Won"] += 0.03
        weights["Lost"] -= 0.01
        weights["Churned"] -= 0.02

    manager_number = int(
        account_manager.split("_")[-1]
    )
    manager_effect = {
        1: 0.03,
        2: 0.015,
        3: 0.00,
        4: -0.015,
        5: -0.03,
    }[manager_number]

    weights["Won"] += manager_effect
    weights["Lost"] -= (
        manager_effect
        * 0.6
    )
    weights["Churned"] -= (
        manager_effect
        * 0.4
    )

    bounded = {
        status: max(value, 0.01)
        for status, value in weights.items()
    }
    total = sum(bounded.values())

    return {
        status: value / total
        for status, value in bounded.items()
    }


def choose_status(
    segment: str,
    product: str,
    order_date: datetime,
    account_manager: str,
) -> str:
    """Sample one synthetic order status."""

    probabilities = status_probabilities(
        segment,
        product,
        order_date,
        account_manager,
    )

    return random.choices(
        population=list(STATUSES),
        weights=[
            probabilities[status]
            for status in STATUSES
        ],
        k=1,
    )[0]


def generate_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    """Generate and save the synthetic customer and order datasets."""

    np.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)

    customers = pd.DataFrame(
        {
            "customer_id": [
                f"C{str(index).zfill(4)}"
                for index in range(
                    1,
                    N_CUSTOMERS + 1,
                )
            ],
            "company_name": [
                f"Company_{index}"
                for index in range(
                    1,
                    N_CUSTOMERS + 1,
                )
            ],
            "region": np.random.choice(
                REGIONS,
                N_CUSTOMERS,
            ),
            "segment": np.random.choice(
                SEGMENTS,
                N_CUSTOMERS,
                p=[0.2, 0.5, 0.3],
            ),
            "since": [
                random_date(
                    START_DATE,
                    END_DATE,
                ).strftime("%Y-%m-%d")
                for _ in range(
                    N_CUSTOMERS
                )
            ],
            "account_manager": [
                f"AM_{random.randint(1, 5)}"
                for _ in range(
                    N_CUSTOMERS
                )
            ],
        }
    )

    rows: list[dict] = []

    for _ in range(N_ORDERS):
        customer = (
            customers
            .sample(1)
            .iloc[0]
        )
        product = random.choice(
            list(PRODUCTS)
        )
        lower_price, upper_price = (
            PRODUCTS[product]
        )

        quantity = random.randint(
            1,
            5,
        )
        unit_price = round(
            random.uniform(
                lower_price,
                upper_price,
            ),
            2,
        )

        customer_since = datetime.strptime(
            customer["since"],
            "%Y-%m-%d",
        )
        order_date = random_date(
            customer_since,
            END_DATE,
        )

        rows.append(
            {
                "order_id": (
                    f"ORD{str(len(rows) + 1).zfill(5)}"
                ),
                "customer_id": customer[
                    "customer_id"
                ],
                "region": customer[
                    "region"
                ],
                "segment": customer[
                    "segment"
                ],
                "account_manager": customer[
                    "account_manager"
                ],
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": round(
                    unit_price
                    * quantity,
                    2,
                ),
                "status": choose_status(
                    customer["segment"],
                    product,
                    order_date,
                    customer[
                        "account_manager"
                    ],
                ),
                "order_date": order_date.strftime(
                    "%Y-%m-%d"
                ),
                "month": order_date.strftime(
                    "%Y-%m"
                ),
                "quarter": (
                    f"{order_date.year}-Q"
                    f"{(order_date.month - 1) // 3 + 1}"
                ),
                "year": order_date.year,
            }
        )

    orders = pd.DataFrame(
        rows
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    customers.to_csv(
        DATA_DIR / "customers.csv",
        index=False,
    )
    orders.to_csv(
        DATA_DIR / "orders.csv",
        index=False,
    )

    return customers, orders


if __name__ == "__main__":
    generated_customers, generated_orders = (
        generate_data()
    )

    print(
        "✓ customers.csv  → "
        f"{len(generated_customers)} rows"
    )
    print(
        "✓ orders.csv     → "
        f"{len(generated_orders)} rows"
    )
