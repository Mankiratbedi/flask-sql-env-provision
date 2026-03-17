# Async Deadlock Hunt

An asyncio job-processing service at `/app/job_processor.py` intermittently hangs under concurrent load. The service processes jobs and manages a shared cache, but deadlocks when both operations run simultaneously.

## Symptoms

Running the workload hangs indefinitely:
```bash
python3 /app/job_processor.py
# hangs and never returns
```

## Your Task

1. Read `/app/job_processor.py` and identify the deadlock
2. Fix the bug in `/app/job_processor.py`
3. Verify the fix works:
   ```bash
   python3 /app/job_processor.py
   # should complete quickly and print a JSON result
   ```

## Requirements

The fixed service must:
- Complete `run_workload(20)` within 5 seconds without deadlocking
- Process all 20 jobs successfully (no errors in the gather result)
- Write the result JSON to `/app/result.json`

## Output

`/app/result.json` must be valid JSON with keys: `total_tasks`, `successes`, `errors`, `processed_jobs`.

The `errors` count must be `0`.
