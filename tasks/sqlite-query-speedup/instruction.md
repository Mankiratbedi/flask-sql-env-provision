# SQLite Query Speedup

A SQLite database at `/app/shop.db` has 200K orders, 10K customers, and 5K products. A set of 5 business queries in `/app/queries.sql` are running too slowly for production use.

## Benchmark

Run the benchmark to see current performance:
```bash
python3 /app/benchmark.py
# Shows timing for each query vs 200ms threshold
```

## Your Task

Optimize the database so all 5 queries in `/app/queries.sql` complete in under **200ms** each.

You may:
- Add indexes to `/app/shop.db` using `sqlite3` or Python
- Rewrite queries in `/app/queries.sql` (must return equivalent results)
- Add computed columns or covering indexes

You must NOT:
- Reduce the dataset (all 200K orders must remain)
- Pre-compute hardcoded answers

## Verification

```bash
python3 /app/benchmark.py
# All 5 queries must show PASS (< 200ms)
```

Results are written to `/app/benchmark_results.json`.

## Schema

```sql
orders(id, customer_id, product_id, quantity, total_price, status, created_at, region)
customers(id, name, email, country, tier)
products(id, name, category, price, supplier_id)
```

## Hint

Start by running `EXPLAIN QUERY PLAN <query>` on the slow queries to identify full table scans.
