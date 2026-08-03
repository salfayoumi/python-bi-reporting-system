
"""
data_analysis.py

Utility script used during the exploratory data analysis (EDA)
phase of the project.

This script inspects the customer and order datasets before the
Business Intelligence pipeline is executed. It is not required
for generating reports and dashboards.
"""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

customers_path = DATA_DIR / "customers.csv"
orders_path = DATA_DIR / "orders.csv"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load customer and order datasets from CSV files."""
    customers = pd.read_csv(customers_path)
    orders = pd.read_csv(orders_path)

    return customers, orders


def inspect_dataframe(name: str, dataframe: pd.DataFrame) -> None:
    """Print basic structural information about a DataFrame."""
    print(f"\n{'=' * 50}")
    print(name)
    print(f"{'=' * 50}")

    print(f"Number of rows: {dataframe.shape[0]}")
    print(f"Number of columns: {dataframe.shape[1]}")

    print("\nFirst five rows:")
    print(dataframe.head())

    print("\nColumn data types:")
    print(dataframe.dtypes)

    print("\nMissing values:")
    print(dataframe.isnull().sum())

    print("\nDuplicate rows:")
    print(dataframe.duplicated().sum())


def main() -> None:
    customers, orders = load_data()

    inspect_dataframe("CUSTOMERS DATASET", customers)
    inspect_dataframe("ORDERS DATASET", orders)

    print("\nCustomer segment distribution:")
    print(customers["segment"].value_counts())

    print("\nCustomer region distribution:")
    print(customers["region"].value_counts())

    print("\nOrder status distribution:")
    print(orders["status"].value_counts())

    print("\nProduct distribution:")
    print(orders["product"].value_counts())

    print("\nTotal order amount statistics:")
    print(orders["total_amount"].describe())


if __name__ == "__main__":
    main()