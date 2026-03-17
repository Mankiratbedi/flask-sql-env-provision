#!/usr/bin/env python3
"""Generate the SQLite benchmark database."""
import sqlite3
import random
from datetime import datetime, timedelta

random.seed(42)

DB_PATH = "/app/shop.db"

REGIONS = ["north", "south", "east", "west", "central"]
STATUSES = ["pending", "shipped", "delivered", "cancelled", "returned"]
TIERS = ["bronze", "silver", "gold", "platinum"]
CATEGORIES = ["electronics", "clothing", "food", "furniture", "sports", "books", "toys"]
COUNTRIES = ["US", "UK", "DE", "FR", "JP", "CA", "AU", "BR", "IN", "MX"]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.executescript("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    country TEXT NOT NULL,
    tier TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    supplier_id INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total_price REAL NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    region TEXT NOT NULL
);
""")

# Insert customers
NUM_CUSTOMERS = 10000
print("Inserting customers...")
customers = [
    (i, f"Customer {i}", f"customer{i}@example.com",
     random.choice(COUNTRIES), random.choice(TIERS))
    for i in range(1, NUM_CUSTOMERS + 1)
]
c.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", customers)

# Insert products
NUM_PRODUCTS = 5000
print("Inserting products...")
products = [
    (i, f"Product {i}", random.choice(CATEGORIES),
     round(random.uniform(5.0, 500.0), 2), random.randint(1, 200))
    for i in range(1, NUM_PRODUCTS + 1)
]
c.executemany("INSERT INTO products VALUES (?,?,?,?,?)", products)

# Insert orders (200K rows, spread over last 90 days)
NUM_ORDERS = 200000
print("Inserting orders...")
base_date = datetime(2026, 3, 16)
batch_size = 10000

for batch_start in range(0, NUM_ORDERS, batch_size):
    batch = []
    for i in range(batch_start + 1, min(batch_start + batch_size + 1, NUM_ORDERS + 1)):
        days_ago = random.randint(0, 89)
        date_str = (base_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        qty = random.randint(1, 20)
        prod_id = random.randint(1, NUM_PRODUCTS)
        price = round(products[prod_id - 1][3] * qty, 2)
        batch.append((
            i,
            random.randint(1, NUM_CUSTOMERS),
            prod_id,
            qty,
            price,
            random.choice(STATUSES),
            date_str,
            random.choice(REGIONS),
        ))
    c.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?)", batch)
    conn.commit()
    print(f"  Inserted {min(batch_start + batch_size, NUM_ORDERS):,} / {NUM_ORDERS:,} orders")

conn.commit()
conn.close()
print(f"Database created at {DB_PATH}")
print(f"  customers: {NUM_CUSTOMERS:,}")
print(f"  products: {NUM_PRODUCTS:,}")
print(f"  orders: {NUM_ORDERS:,}")
