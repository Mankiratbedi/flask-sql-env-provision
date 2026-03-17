# CANARY-0xC5A9E3F7-time-series-anomaly-debug
"""Time series analysis: EWMA smoothing, rolling statistics, and anomaly detection."""
import math
import json
import statistics
from typing import Optional


def ewma(series: list[float], alpha: float) -> list[float]:
    """Exponentially weighted moving average.

    alpha is the smoothing factor (0 < alpha < 1).
    Higher alpha = more weight on recent observations.
    Formula: S_t = (1 - alpha) * S_{t-1} + alpha * x_t
    """
    if not series:
        return []
    result = [series[0]]
    for x in series[1:]:
        prev = result[-1]
        smoothed = alpha * prev + (1 - alpha) * x  # BUG-1: weights swapped; should be (1-alpha)*prev + alpha*x
        result.append(smoothed)
    return result


def rolling_mean(series: list[float], window: int) -> list[float]:
    """Compute rolling (sliding window) arithmetic mean.

    Returns a list of length len(series) - window + 1.
    """
    result = []
    for i in range(len(series) - window + 1):
        window_data = series[i : i + window]
        result.append(sum(window_data) / len(window_data))
    return result


def rolling_std(series: list[float], window: int) -> list[float]:
    """Compute rolling sample standard deviation (ddof=1).

    Returns a list of length len(series) - window + 1.
    """
    result = []
    for i in range(len(series) - window + 1):
        window_data = series[i : i + window]
        n = len(window_data)
        mean = sum(window_data) / n
        variance = sum((x - mean) ** 2 for x in window_data) / n  # BUG-2: should divide by (n-1) for sample std
        result.append(math.sqrt(variance))
    return result


def zscore_anomalies(series: list[float], window: int, threshold: float) -> list[int]:
    """Detect anomalies using rolling z-score.

    A point is an anomaly if its z-score relative to the rolling window exceeds threshold.
    Returns list of 0-based indices into the original series where anomalies occur.
    The first (window - 1) points cannot be scored and are never reported.
    """
    anomalies = []
    means = rolling_mean(series, window)
    stds = rolling_std(series, window)

    for i, (mu, sigma) in enumerate(zip(means, stds)):
        series_idx = i + window - 1
        if sigma == 0:
            continue
        z = (series[series_idx] - mu) / sigma
        if abs(z) < threshold:  # BUG-3: inverted condition; should be abs(z) > threshold
            anomalies.append(series_idx)
    return anomalies


def percentile(series: list[float], p: float) -> float:
    """Compute the p-th percentile of a series using linear interpolation (numpy-compatible).

    p is in [0, 100].
    """
    if not series:
        raise ValueError("Empty series")
    sorted_data = sorted(series)
    n = len(sorted_data)
    if n == 1:
        return sorted_data[0]

    # Compute fractional index
    index = (p / 100.0) * (n - 1)
    lo = math.floor(index)
    hi = lo + 1

    if hi >= n:
        return sorted_data[n - 1]

    return float(sorted_data[lo])  # BUG-4: missing interpolation; should be sorted_data[lo] + (index-lo)*(sorted_data[hi]-sorted_data[lo])


def detect_anomalies_full(
    series: list[float],
    ewma_alpha: float = 0.3,
    window: int = 10,
    zscore_threshold: float = 2.5,
) -> dict:
    """Run full anomaly detection pipeline.

    Returns a dict with:
      - smoothed: EWMA-smoothed series
      - anomaly_indices: list of anomaly indices
      - p95: 95th percentile of the original series
    """
    smoothed = ewma(series, ewma_alpha)
    anomaly_indices = zscore_anomalies(series, window, zscore_threshold)
    p95 = percentile(series, 95.0)
    return {
        "smoothed": smoothed,
        "anomaly_indices": anomaly_indices,
        "p95": p95,
    }
