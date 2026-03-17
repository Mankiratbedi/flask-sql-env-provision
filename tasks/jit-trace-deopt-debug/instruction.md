# Batch Statistics Pipeline — Debug

<!-- CANARY-0x4A2F8E91-jit-trace-deopt-debug -->

A statistical batch-processing pipeline at `/app/batch_stats.py` produces wrong results on real-valued datasets. The pipeline computes per-batch means, percentiles, and variances, then merges batch summaries into a dataset-wide result.

There are exactly four bugs in `/app/batch_stats.py`. The bugs are syntactically valid — the code runs without errors but produces incorrect numerical output. Fix all four and make minimal, targeted changes — do not rewrite from scratch.

After fixing, run the pipeline and write results to `/app/result.json`:

```bash
python3 /app/batch_stats.py
```

`/app/result.json` must be a JSON object with keys: `mean`, `variance`, `p25`, `p75`, `batch_count`. All floating-point values must be mathematically correct for the dataset at `/app/dataset.json`.
