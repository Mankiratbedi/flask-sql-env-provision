FROM python:3.12-slim
# CANARY-0x2E3F4A5B-sql-plan-regression

RUN apt-get update && apt-get install -y tmux && rm -rf /var/lib/apt/lists/*

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

# Install dependencies system-wide to avoid networking issues during test runs
RUN uv pip install --system pytest==8.4.1 pytest-json-ctrf==0.3.5

WORKDIR /app

COPY sql_planner.py /app/sql_planner.py

# Generate schema and queries
RUN python3 -c 'import json; \
    schema = {"tables": [{"name": "orders", "stats": {"row_count": 1000000, "page_size": 8192, "stats_version": 5}}, {"name": "users", "stats": {"row_count": 50000, "page_size": 8192, "stats_version": 5}}, {"name": "products", "stats": {"row_count": 10000, "page_size": 8192, "stats_version": 5}}], "indexes": [{"table": "orders", "column": "customer_id", "type": "btree"}, {"table": "users", "column": "email", "type": "expression"}, {"table": "products", "column": "category_id", "type": "btree"}]}; \
    queries = [{"id": 1, "table": "orders", "predicate": {"column": "customer_id", "op": "eq", "selectivity": 0.001}, "stats_version": 5}, {"id": 2, "table": "users", "predicate": {"column": "email", "op": "eq", "selectivity": 0.0001}, "stats_version": 5}, {"id": 3, "table": "users", "predicate": {"column": "email", "op": "gt", "selectivity": 0.5}, "stats_version": 5}, {"id": 4, "table": "products", "predicate": {"column": "category_id", "op": "eq", "selectivity": 0.05}, "stats_version": 3}, {"id": 5, "table": "orders", "predicate": {"column": "total_amount", "op": "gt", "selectivity": 0.8}, "stats_version": 5}]; \
    json.dump(schema, open("/app/schema.json", "w")); \
    json.dump(queries, open("/app/queries.json", "w")); \
    print("Schema and queries generated")'
