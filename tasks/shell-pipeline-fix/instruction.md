# Shell Pipeline Fix

A bash script `/app/analyze_logs.sh` processes nginx access logs but produces incorrect output due to multiple bugs. The log file is at `/app/access.log`.

## Running the Script

```bash
bash /app/analyze_logs.sh /app/access.log
cat /app/report.txt
```

## Your Task

Find and fix **all bugs** in `/app/analyze_logs.sh` so the report at `/app/report.txt` is correct.

The report must produce accurate values for:
1. **HTTP methods** — correctly identify GET/POST/PUT/DELETE counts
2. **Top IPs** — correctly count requests per IP (including non-consecutive occurrences)
3. **HTTP status codes** — correctly count each status code (this section currently outputs nothing useful)
4. **Daily request count** — correctly count requests for `15/Mar/2026` (the main log day)
5. **Error rate percentage** — show the correct decimal percentage (e.g., `12.50%` not `12%`)

## Deliverable

Fixed `/app/analyze_logs.sh` that runs without errors and produces correct output.

After fixing, run:
```bash
bash /app/analyze_logs.sh /app/access.log
```

The report will be written to `/app/report.txt`.
