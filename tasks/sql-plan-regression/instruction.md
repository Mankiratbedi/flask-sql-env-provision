# SQL Query Planner — Debug

<!-- CANARY-0x2E3F4A5B-sql-plan-regression -->

A Python SQL query-planner simulator at `/app/sql_planner.py` models how a database engine chooses between sequential scans and index scans for queries. The planner reads a schema from `/app/schema.json` and a set of queries from `/app/queries.json`, then produces an execution plan and cost estimate for each query.

There are exactly four bugs in `/app/sql_planner.py`. The bugs are syntactically valid — the planner runs without errors but chooses wrong plans and computes wrong cost estimates. Fix all four and make minimal, targeted changes — do not rewrite from scratch.

After fixing, run the planner and write results to `/app/plan_results.json`:

```bash
python3 /app/sql_planner.py
```

`/app/plan_results.json` must be a JSON array. Each element must be an object with keys: `query_id` (int), `plan` (string: `"index_scan"` or `"seq_scan"`), `estimated_cost` (float), `result_rows` (int).
