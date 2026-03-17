# Time Series Anomaly Debug

<!-- CANARY-0xC5A9E3F7-time-series-anomaly-debug -->

The time series analysis library at `/app/ts_analysis.py` implements EWMA smoothing, rolling statistics, and z-score-based anomaly detection. There are exactly four bugs in the implementation. Fix all four bugs in `/app/ts_analysis.py`. Make minimal, targeted fixes — do not rewrite from scratch.

The bugs are in:
- `ewma`: the smoothing factor alpha is applied to the wrong term (weights are swapped)
- `rolling_std`: uses a biased variance estimator (divides by n instead of n-1)
- `zscore_anomalies`: the threshold comparison is inverted
- `percentile`: missing linear interpolation between the two surrounding values
