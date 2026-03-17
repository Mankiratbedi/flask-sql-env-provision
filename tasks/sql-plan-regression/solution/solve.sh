#!/bin/bash
set -euo pipefail
# CANARY-0x2E3F4A5B-sql-plan-regression

cd /app

cat > /app/sql_planner.py << 'EOF'
#!/usr/bin/env python3
# CANARY-0x2E3F4A5B-sql-plan-regression
"""SQL query planner simulator — chooses index vs seq scan and estimates cost."""

import json
import math

SCHEMA_PATH = "/app/schema.json"
QUERIES_PATH = "/app/queries.json"
OUTPUT_PATH = "/app/plan_results.json"


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def load_queries():
    with open(QUERIES_PATH) as f:
        return json.load(f)


def stats_are_fresh(table_stats, query_stats_version):
    """Check if table statistics are recent enough to use for planning."""
    # FIXED: use >= to accept current or newer stats
    return table_stats["stats_version"] >= query_stats_version


def matches_index(index_def, predicate):
    """Check if a query predicate can use this index."""
    col = predicate.get("column")
    op = predicate.get("op")
    if index_def["type"] == "expression":
        # FIXED: expression indexes require exact equality match
        return index_def["column"] == col and op == "eq"
    return index_def["column"] == col and op in ("eq", "lt", "gt", "lte", "gte")


def estimate_seq_scan_cost(num_rows, page_size):
    """Estimate sequential scan cost in I/O units."""
    # FIXED: use page_size parameter instead of hardcoded block size
    return math.ceil(num_rows * 100 / page_size)


def estimate_index_scan_cost(num_rows, selectivity):
    """Estimate index scan cost — proportional to rows returned."""
    return math.ceil(num_rows * selectivity * 2)


def choose_plan(table, index_def, predicate, stats_version):
    """Choose between seq_scan and index_scan based on cost estimates."""
    stats = table["stats"]
    num_rows = stats["row_count"]
    page_size = stats["page_size"]
    selectivity = predicate.get("selectivity", 0.1)

    use_fresh_stats = stats_are_fresh(stats, stats_version)
    effective_rows = num_rows if use_fresh_stats else num_rows * 2

    can_use_index = index_def is not None and matches_index(index_def, predicate)

    seq_cost = estimate_seq_scan_cost(effective_rows, page_size)
    idx_cost = estimate_index_scan_cost(effective_rows, selectivity) if can_use_index else float("inf")

    # FIXED: choose index scan when it is cheaper than seq scan
    if can_use_index and idx_cost < seq_cost:
        plan = "index_scan"
        cost = idx_cost
    else:
        plan = "seq_scan"
        cost = seq_cost

    result_rows = math.ceil(effective_rows * selectivity)
    return plan, cost, result_rows


def run_planner():
    schema = load_schema()
    queries = load_queries()
    results = []
    tables = {t["name"]: t for t in schema["tables"]}
    indexes = {idx["table"]: idx for idx in schema.get("indexes", [])}

    for q in queries:
        table = tables[q["table"]]
        index_def = indexes.get(q["table"])
        plan, cost, result_rows = choose_plan(
            table, index_def, q["predicate"], q["stats_version"]
        )
        results.append({
            "query_id": q["id"],
            "plan": plan,
            "estimated_cost": float(cost),
            "result_rows": result_rows,
        })

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f)
    print(f"Done: {len(results)} queries planned")


if __name__ == "__main__":
    run_planner()
EOF

python3 /app/sql_planner.py
echo "Oracle solution complete."
