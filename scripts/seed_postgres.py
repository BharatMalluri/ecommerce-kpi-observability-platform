"""
seed_postgres.py
Generates synthetic e-commerce data and loads it into raw schema.
Run: python scripts/seed_postgres.py
"""
import os
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text

fake = Faker()
random.seed(42)
Faker.seed(42)

# ── Connection ────────────────────────────────────────────────────────────────
DB_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER','admin')}:"
    f"{os.getenv('POSTGRES_PASSWORD','changeme')}@"
    f"{os.getenv('POSTGRES_HOST','localhost')}:"
    f"{os.getenv('POSTGRES_PORT','5432')}/"
    f"{os.getenv('POSTGRES_DB','ecommerce')}"
)
engine = create_engine(DB_URL)

# ── Helpers ───────────────────────────────────────────────────────────────────
COUNTRIES   = ["DE", "AT", "CH", "FR", "NL", "PL", "ES", "IT"]
STATUSES    = ["completed", "completed", "completed", "pending", "cancelled", "refunded"]
CATEGORIES  = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys"]

def random_date(start_days_ago=365):
    return datetime.now() - timedelta(days=random.randint(0, start_days_ago))

# ── Generate data ─────────────────────────────────────────────────────────────
N_CUSTOMERS = 500
N_PRODUCTS  = 80
N_ORDERS    = 3000

print(f"Generating {N_CUSTOMERS} customers...")
customers = pd.DataFrame([{
    "customer_id":  f"CUST-{str(i).zfill(5)}",
    "name":         fake.name(),
    "email":        fake.email(),
    "signup_date":  random_date(730),
    "country":      random.choice(COUNTRIES),
} for i in range(1, N_CUSTOMERS + 1)])

print(f"Generating {N_PRODUCTS} products...")
products = pd.DataFrame([{
    "product_id": f"PROD-{str(i).zfill(4)}",
    "name":       fake.bs().title(),
    "category":   random.choice(CATEGORIES),
    "price":      round(random.uniform(5.0, 499.99), 2),
} for i in range(1, N_PRODUCTS + 1)])

print(f"Generating {N_ORDERS} orders...")
orders = pd.DataFrame([{
    "order_id":    f"ORD-{str(i).zfill(6)}",
    "customer_id": random.choice(customers["customer_id"].tolist()),
    "order_date":  random_date(365),
    "status":      random.choice(STATUSES),
    "amount":      round(random.uniform(10.0, 999.99), 2),
    "product_id":  random.choice(products["product_id"].tolist()),
    "quantity":    random.randint(1, 10),
    "country":     random.choice(COUNTRIES),
} for i in range(1, N_ORDERS + 1)])

# Introduce some intentional quality issues for GE to catch
orders.loc[orders.sample(frac=0.02).index, "amount"] = None      # 2% nulls
orders.loc[orders.sample(frac=0.01).index, "status"] = "UNKNOWN" # invalid status

# ── Load ──────────────────────────────────────────────────────────────────────
with engine.begin() as conn:
    conn.execute(text("TRUNCATE raw.customers, raw.products, raw.orders"))

customers.to_sql("customers", engine, schema="raw", if_exists="append", index=False)
products.to_sql("products",  engine, schema="raw", if_exists="append", index=False)
orders.to_sql("orders",      engine, schema="raw", if_exists="append", index=False)

print(f"✅ Loaded: {len(customers)} customers, {len(products)} products, {len(orders)} orders into raw schema.")
