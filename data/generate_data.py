"""
generate_data.py
Generates a realistic synthetic CRM sales dataset.
Run once: python data/generate_data.py
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

# ── Config ────────────────────────────────────────────────────────────────────
N_CUSTOMERS   = 200
N_ORDERS      = 1500
START_DATE    = datetime(2023, 1, 1)
END_DATE      = datetime(2024, 12, 31)

REGIONS       = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"]
SEGMENTS      = ["Enterprise", "SMB", "Startup"]
PRODUCTS      = {
    "CRM Basic":      (299,  599),
    "CRM Pro":        (799,  1499),
    "CRM Enterprise": (2000, 4999),
    "Support Pack":   (150,  400),
    "Training":       (200,  600),
}
STATUSES      = ["Won", "Won", "Won", "Lost", "Churned"]   # weighted


def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


# ── Customers ─────────────────────────────────────────────────────────────────
customers = pd.DataFrame({
    "customer_id":  [f"C{str(i).zfill(4)}" for i in range(1, N_CUSTOMERS + 1)],
    "company_name": [f"Company_{i}" for i in range(1, N_CUSTOMERS + 1)],
    "region":       np.random.choice(REGIONS,    N_CUSTOMERS),
    "segment":      np.random.choice(SEGMENTS,   N_CUSTOMERS, p=[0.2, 0.5, 0.3]),
    "since":        [random_date(START_DATE, END_DATE).strftime("%Y-%m-%d")
                     for _ in range(N_CUSTOMERS)],
    "account_manager": [f"AM_{random.randint(1,5)}" for _ in range(N_CUSTOMERS)],
})

# ── Orders ────────────────────────────────────────────────────────────────────
rows = []
for _ in range(N_ORDERS):
    cust   = customers.sample(1).iloc[0]
    prod   = random.choice(list(PRODUCTS.keys()))
    lo, hi = PRODUCTS[prod]
    qty    = random.randint(1, 5)
    price  = round(random.uniform(lo, hi), 2)
    date   = random_date(START_DATE, END_DATE)
    rows.append({
        "order_id":     f"ORD{str(len(rows)+1).zfill(5)}",
        "customer_id":  cust["customer_id"],
        "region":       cust["region"],
        "segment":      cust["segment"],
        "account_manager": cust["account_manager"],
        "product":      prod,
        "quantity":     qty,
        "unit_price":   price,
        "total_amount": round(price * qty, 2),
        "status":       random.choice(STATUSES),
        "order_date":   date.strftime("%Y-%m-%d"),
        "month":        date.strftime("%Y-%m"),
        "quarter":      f"{date.year}-Q{(date.month-1)//3+1}",
        "year":         date.year,
    })

orders = pd.DataFrame(rows)

customers.to_csv("data/customers.csv", index=False)
orders.to_csv("data/orders.csv",       index=False)

print(f"✓ customers.csv  → {len(customers)} rows")
print(f"✓ orders.csv     → {len(orders)} rows")
