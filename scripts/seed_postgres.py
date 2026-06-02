import os
import random
from datetime import datetime, timedelta
from io import StringIO

import pandas as pd
from faker import Faker
import psycopg2

fake = Faker()
random.seed(42)
Faker.seed(42)

COUNTRIES  = ["DE", "AT", "CH", "FR", "NL", "PL", "ES", "IT"]
STATUSES   = ["completed", "completed", "completed", "pending", "cancelled", "refunded"]
CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys"]

def random_date(days=365):
    return datetime.now() - timedelta(days=random.randint(0, days))

print("Generating 500 customers...")
customers = pd.DataFrame([{
    "customer_id": f"CUST-{str(i).zfill(5)}",
    "name":        fake.name(),
    "email":       fake.email(),
    "signup_date": random_date(730),
    "country":     random.choice(COUNTRIES),
} for i in range(1, 501)])

print("Generating 80 products...")
products = pd.DataFrame([{
    "product_id": f"PROD-{str(i).zfill(4)}",
    "name":       fake.bs().title(),
    "category":   random.choice(CATEGORIES),
    "price":      round(random.uniform(5.0, 499.99), 2),
} for i in range(1, 81)])

print("Generating 3000 orders...")
orders = pd.DataFrame([{
    "order_id":    f"ORD-{str(i).zfill(6)}",
    "customer_id": random.choice(customers["customer_id"].tolist()),
    "order_date":  random_date(365),
    "status":      random.choice(STATUSES),
    "amount":      round(random.uniform(10.0, 999.99), 2),
    "product_id":  random.choice(products["product_id"].tolist()),
    "quantity":    random.randint(1, 10),
    "country":     random.choice(COUNTRIES),
} for i in range(1, 3001)])

orders.loc[orders.sample(frac=0.02).index, "amount"] = None
orders.loc[orders.sample(frac=0.01).index, "status"] = "UNKNOWN"

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5433")),
    dbname=os.getenv("POSTGRES_DB", "ecommerce"),
    user=os.getenv("POSTGRES_USER", "admin"),
    password=os.getenv("POSTGRES_PASSWORD", "changeme"),
)
cur = conn.cursor()
cur.execute("TRUNCATE raw.customers, raw.products, raw.orders")

def copy_df(df, table):
    buf = StringIO()
    df.to_csv(buf, index=False, header=False, na_rep="")
    buf.seek(0)
    cols = ",".join(df.columns)
    cur.copy_expert(f"COPY raw.{table} ({cols}) FROM STDIN WITH CSV", buf)

copy_df(customers, "customers")
copy_df(products, "products")
copy_df(orders, "orders")

conn.commit()
cur.close()
conn.close()

print("Loaded: 500 customers, 80 products, 3000 orders into raw schema.")