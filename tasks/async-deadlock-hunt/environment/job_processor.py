#!/usr/bin/env python3
"""Async job processing service.

Processes jobs concurrently using a shared resource pool and cache.
Has a subtle lock-ordering bug that causes deadlocks under concurrent load.
"""
import asyncio
import hashlib

# Two locks protecting shared state
resource_lock = asyncio.Lock()
cache_lock = asyncio.Lock()

# Shared state
resource_pool: dict[str, str] = {}
cache: dict[str, str] = {}
processed_jobs: list[str] = []


async def fetch_resource(job_id: str) -> str:
    """Fetch or create a resource for the job."""
    if job_id not in resource_pool:
        # Simulate resource creation
        await asyncio.sleep(0.001)
        resource_pool[job_id] = hashlib.md5(job_id.encode()).hexdigest()
    return resource_pool[job_id]


async def process_job(job_id: str) -> str:
    """Process a single job. Acquires resource_lock then cache_lock."""
    async with resource_lock:                    # Lock order: resource first
        resource = await fetch_resource(job_id)
        async with cache_lock:                   # Lock order: cache second
            result = f"result:{resource[:8]}"
            cache[job_id] = result
            processed_jobs.append(job_id)
            return result


async def invalidate_cache(pattern: str) -> int:
    """Invalidate cache entries matching pattern. BUG: acquires locks in wrong order."""
    async with cache_lock:                       # BUG: cache first  ← wrong order!
        await asyncio.sleep(0.001)               # Simulate work
        async with resource_lock:                # BUG: resource second ← wrong order!
            keys_to_remove = [k for k in cache if pattern in k]
            for k in keys_to_remove:
                del cache[k]
            return len(keys_to_remove)


async def run_workload(num_jobs: int = 20) -> dict:
    """Run a mixed workload of job processing and cache invalidation."""
    job_ids = [f"job_{i:04d}" for i in range(num_jobs)]

    # Interleave process_job and invalidate_cache calls — this triggers the deadlock
    tasks = []
    for i, job_id in enumerate(job_ids):
        tasks.append(asyncio.create_task(process_job(job_id)))
        if i % 5 == 4:
            tasks.append(asyncio.create_task(invalidate_cache("job_")))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    errors = [r for r in results if isinstance(r, Exception)]
    successes = [r for r in results if isinstance(r, str)]

    return {
        "total_tasks": len(tasks),
        "successes": len(successes),
        "errors": len(errors),
        "processed_jobs": len(processed_jobs),
    }


if __name__ == "__main__":
    import json
    result = asyncio.run(asyncio.wait_for(run_workload(20), timeout=5.0))
    print(json.dumps(result))
