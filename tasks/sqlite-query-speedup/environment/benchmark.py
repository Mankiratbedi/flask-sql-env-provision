#!/usr/bin/env python3
"""Benchmark the 5 queries and output timing results."""
import sqlite3
import time
import json
import sys

DB_PATH = "/app/shop.db"
QUERIES_PATH = "/app/queries.sql"
THRESHOLD_MS = 200.0


def parse_queries(sql_text: str) -> list[tuple[str, str]]:
    """Parse queries.sql into (name, sql) pairs."""
    queries = []
    current_comment = ""
    current_sql = []
    for line in sql_text.split("\n"):
        if line.strip().startswith("-- Q"):
            if current_sql:
                queries.append((current_comment, " ".join(current_sql).strip()))
            current_comment = line.strip().lstrip("- ").strip()
            current_sql = []
        elif line.strip():
            current_sql.append(line)
    if current_sql:
        queries.append((current_comment, " ".join(current_sql).strip()))
    return queries


def benchmark():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    with open(QUERIES_PATH) as f:
        sql_text = f.read()

    queries = parse_queries(sql_text)
    results = []
    all_passed = True

    for name, sql in queries:
        # Warm up
        conn.execute(sql).fetchall()
        # Timed run (average of 3)
        times = []
        for _ in range(3):
            start = time.perf_counter()
            rows = conn.execute(sql).fetchall()
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        avg_ms = sum(times) / len(times)
        passed = avg_ms < THRESHOLD_MS
        if not passed:
            all_passed = False

        results.append({
            "query": name,
            "avg_ms": round(avg_ms, 1),
            "threshold_ms": THRESHOLD_MS,
            "passed": passed,
            "rows_returned": len(rows),
        })
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}: {avg_ms:.1f}ms ({len(rows)} rows)")

    conn.close()

    with open("/app/benchmark_results.json", "w") as f:
        json.dump({"queries": results, "all_passed": all_passed}, f, indent=2)

    return all_passed


if __name__ == "__main__":
    ok = benchmark()
    sys.exit(0 if ok else 1)
