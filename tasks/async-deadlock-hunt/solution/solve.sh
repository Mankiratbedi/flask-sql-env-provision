#!/bin/bash
set -euo pipefail

python3 - << 'PYEOF'
with open('/app/job_processor.py', 'r') as f:
    src = f.read()

# Fix: acquire resource_lock before cache_lock in invalidate_cache (same order as process_job)
old = '''async def invalidate_cache(pattern: str) -> int:
    """Invalidate cache entries matching pattern. BUG: acquires locks in wrong order."""
    async with cache_lock:                       # BUG: cache first  ← wrong order!
        await asyncio.sleep(0.001)               # Simulate work
        async with resource_lock:                # BUG: resource second ← wrong order!'''
new = '''async def invalidate_cache(pattern: str) -> int:
    """Invalidate cache entries matching pattern. Fixed: consistent lock order."""
    async with resource_lock:                    # FIX: resource first (same as process_job)
        await asyncio.sleep(0.001)               # Simulate work
        async with cache_lock:                   # FIX: cache second (same as process_job)'''

assert old in src, "Could not find bug pattern"
fixed = src.replace(old, new, 1)
with open('/app/job_processor.py', 'w') as f:
    f.write(fixed)
print("Fixed: lock order now consistent in invalidate_cache")
PYEOF

python3 -c "
import asyncio, json
import sys
sys.path.insert(0, '/app')
from job_processor import run_workload
result = asyncio.run(asyncio.wait_for(run_workload(20), timeout=5.0))
with open('/app/result.json', 'w') as f:
    import json
    json.dump(result, f)
print('Result:', result)
"
