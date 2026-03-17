#!/bin/bash
set -euo pipefail
# CANARY-0x4A2F8E91-jit-trace-deopt-debug

cd /app

python3 << 'PATCH'
with open("/app/batch_stats.py") as f:
    src = f.read()

# Fix Bug-1: int() truncation in accumulation
src = src.replace(
    "        total = int(total + v)  # BUG-1: int() truncates fractional accumulation",
    "        total += v"
)

# Fix Bug-2: percentile index multiplier
src = src.replace(
    "    idx = math.floor(p / 100.0 * n)  # BUG-2: should be (n - 1), not n",
    "    idx = math.floor(p / 100.0 * (n - 1))  # FIXED: correct percentile index"
)

# Fix Bug-3: population variance (Bessel's correction)
src = src.replace(
    "    return sum(sq_diffs) / len(values)  # BUG-3: should divide by len(values) - 1",
    "    return sum(sq_diffs) / (len(values) - 1)  # FIXED: Bessel's correction"
)

# Fix Bug-4: unweighted merge
src = src.replace(
    "    merged_mean = (stats_a[\"mean\"] + stats_b[\"mean\"]) / 2  # BUG-4: unweighted; should be (na*ma + nb*mb) / (na+nb)",
    "    merged_mean = (na * stats_a[\"mean\"] + nb * stats_b[\"mean\"]) / (na + nb)  # FIXED: weighted mean"
)

assert "BUG-" not in src, "Not all bugs were fixed!"
with open("/app/batch_stats.py", "w") as f:
    f.write(src)
print("All four bugs fixed.")
PATCH

python3 /app/batch_stats.py
echo "Oracle solution complete."
