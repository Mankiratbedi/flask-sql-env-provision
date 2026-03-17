#!/bin/bash
set -euo pipefail

python3 - << 'PYEOF'
import sqlite3

conn = sqlite3.connect("/app/shop.db")

# Add covering indexes for the most common query patterns
indexes = [
    # Q1, Q5: filter by created_at, group by region/customer
    "CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_orders_customer_created ON orders(customer_id, created_at, total_price)",
    "CREATE INDEX IF NOT EXISTS idx_orders_product_created ON orders(product_id, created_at, quantity)",
    "CREATE INDEX IF NOT EXISTS idx_orders_region_created ON orders(region, created_at, total_price)",
    # Q3: group by region, status
    "CREATE INDEX IF NOT EXISTS idx_orders_region_status ON orders(region, status, total_price)",
    # Q4: filter by tier, join to orders
    "CREATE INDEX IF NOT EXISTS idx_customers_tier ON customers(tier, id)",
    "CREATE INDEX IF NOT EXISTS idx_orders_customer_price ON orders(customer_id, total_price)",
    # Q2: product category lookups
    "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
]

for idx in indexes:
    print(f"Creating: {idx[:60]}...")
    conn.execute(idx)

conn.commit()

# Optimize the database
conn.execute("ANALYZE")
conn.commit()
conn.close()
print("All indexes created and statistics updated")
PYEOF

python3 /app/benchmark.py
