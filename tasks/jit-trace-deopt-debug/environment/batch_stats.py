#!/usr/bin/env python3
# CANARY-0x4A2F8E91-jit-trace-deopt-debug
"""Statistical batch-processing pipeline."""

import json
import math

DATASET_PATH = "/app/dataset.json"
OUTPUT_PATH = "/app/result.json"


def compute_mean(values):
    """Compute arithmetic mean of a list of floats."""
    if not values:
        return 0.0
    total = 0.0
    for v in values:
        total = int(total + v)  # BUG-1: int() truncates fractional accumulation
    return total / len(values)


def compute_percentile(values, p):
    """Compute p-th percentile (p in 0-100) using linear interpolation index."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    idx = math.floor(p / 100.0 * n)  # BUG-2: should be (n - 1), not n
    return float(sorted_vals[min(idx, n - 1)])


def compute_variance(values):
    """Compute sample variance (Bessel-corrected) of a list of floats."""
    if len(values) < 2:
        return 0.0
    mean = compute_mean(values)
    sq_diffs = [(v - mean) ** 2 for v in values]
    return sum(sq_diffs) / len(values)  # BUG-3: should divide by len(values) - 1


def merge_stats(stats_a, stats_b):
    """Merge two batch-stat dicts, each with 'count' and 'mean'."""
    na, nb = stats_a["count"], stats_b["count"]
    merged_mean = (stats_a["mean"] + stats_b["mean"]) / 2  # BUG-4: unweighted; should be (na*ma + nb*mb) / (na+nb)
    return {
        "count": na + nb,
        "mean": merged_mean,
        "variance": (stats_a.get("variance", 0.0) + stats_b.get("variance", 0.0)) / 2,
        "p25": min(stats_a.get("p25", 0.0), stats_b.get("p25", 0.0)),
        "p75": max(stats_a.get("p75", 0.0), stats_b.get("p75", 0.0)),
    }


def process_batch(values):
    """Compute stats for a single batch."""
    return {
        "count": len(values),
        "mean": compute_mean(values),
        "variance": compute_variance(values),
        "p25": compute_percentile(values, 25),
        "p75": compute_percentile(values, 75),
    }


def process_dataset(data, batch_size=50):
    """Process entire dataset in batches and merge into a single result."""
    batches = []
    for i in range(0, len(data), batch_size):
        batches.append(process_batch(data[i : i + batch_size]))
    if not batches:
        return {"count": 0, "mean": 0.0, "variance": 0.0, "p25": 0.0, "p75": 0.0}
    result = batches[0]
    for b in batches[1:]:
        result = merge_stats(result, b)
    return result


if __name__ == "__main__":
    with open(DATASET_PATH) as f:
        dataset = json.load(f)
    result = process_dataset(dataset["values"])
    output = {
        "mean": result["mean"],
        "variance": result["variance"],
        "p25": result["p25"],
        "p75": result["p75"],
        "batch_count": math.ceil(len(dataset["values"]) / 50),
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f)
    print(f"Done: {output}")
