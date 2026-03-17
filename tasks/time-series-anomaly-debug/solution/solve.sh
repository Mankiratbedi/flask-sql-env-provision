#!/bin/bash
set -euo pipefail
# CANARY-0xC5A9E3F7-time-series-anomaly-debug

python3 - << 'PYEOF'
with open('/app/ts_analysis.py', 'r') as f:
    src = f.read()

# Fix BUG-1: EWMA alpha weights are swapped
old1 = '        smoothed = alpha * prev + (1 - alpha) * x  # BUG-1: weights swapped; should be (1-alpha)*prev + alpha*x'
new1 = '        smoothed = (1 - alpha) * prev + alpha * x'
assert old1 in src, "BUG-1 pattern not found"
src = src.replace(old1, new1, 1)

# Fix BUG-2: rolling_std uses biased estimator (divide by n not n-1)
old2 = '        variance = sum((x - mean) ** 2 for x in window_data) / n  # BUG-2: should divide by (n-1) for sample std'
new2 = '        variance = sum((x - mean) ** 2 for x in window_data) / (n - 1)'
assert old2 in src, "BUG-2 pattern not found"
src = src.replace(old2, new2, 1)

# Fix BUG-3: anomaly condition is inverted
old3 = '        if abs(z) < threshold:  # BUG-3: inverted condition; should be abs(z) > threshold'
new3 = '        if abs(z) > threshold:'
assert old3 in src, "BUG-3 pattern not found"
src = src.replace(old3, new3, 1)

# Fix BUG-4: percentile missing linear interpolation
old4 = '    return float(sorted_data[lo])  # BUG-4: missing interpolation; should be sorted_data[lo] + (index-lo)*(sorted_data[hi]-sorted_data[lo])'
new4 = '    return float(sorted_data[lo] + (index - lo) * (sorted_data[hi] - sorted_data[lo]))'
assert old4 in src, "BUG-4 pattern not found"
src = src.replace(old4, new4, 1)

with open('/app/ts_analysis.py', 'w') as f:
    f.write(src)
print("All 4 bugs fixed.")
PYEOF
