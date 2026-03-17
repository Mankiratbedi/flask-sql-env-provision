#!/usr/bin/env python3
# CANARY-0x9C1D2E3F-cache-coherence-sim
"""MESI cache-coherence protocol simulator for 4 processors."""

import json

OUTPUT_PATH = "/app/result.json"
TRACE_PATHS = {
    "trace_a": "/app/traces/trace_a.json",
    "trace_b": "/app/traces/trace_b.json",
    "trace_c": "/app/traces/trace_c.json",
}

INVALID, SHARED, EXCLUSIVE, MODIFIED = "I", "S", "E", "M"


class CacheLine:
    def __init__(self):
        self.state = INVALID
        self.data = None
        self.address = None


class Cache:
    def __init__(self, pid, size=4):
        self.pid = pid
        self.size = size
        self.lines = [CacheLine() for _ in range(size)]
        self.lru = list(range(size))  # lru[0] = least recently used

    def find(self, address):
        for i, line in enumerate(self.lines):
            if line.state != INVALID and line.address == address:
                return i
        return -1

    def evict_lru(self):
        return self.lru[0]

    def touch(self, idx):
        if idx in self.lru:
            self.lru.remove(idx)
        self.lru.append(idx)


class MESISimulator:
    def __init__(self, num_procs=4):
        self.caches = [Cache(i) for i in range(num_procs)]
        self.memory = {}

    def _writeback(self, cache, idx):
        line = cache.lines[idx]
        if line.state == MODIFIED and line.address is not None:
            self.memory[line.address] = line.data

    def _invalidate_others(self, requesting_pid, address, keep_shared=False):
        for pid, cache in enumerate(self.caches):
            if pid == requesting_pid:
                continue
            idx = cache.find(address)
            if idx != -1:
                line = cache.lines[idx]
                if line.state == MODIFIED:
                    self.memory[address] = line.data
                if keep_shared and line.state in (SHARED, EXCLUSIVE):
                    line.state = SHARED
                else:
                    line.state = INVALID

    def read(self, pid, address):
        cache = self.caches[pid]
        idx = cache.find(address)
        if idx != -1:
            line = cache.lines[idx]
            # BUG-1: EXCLUSIVE hit should downgrade to SHARED if others may snoop,
            # but here we skip the snoop and stay in EXCLUSIVE when we should go SHARED
            if line.state in (EXCLUSIVE, MODIFIED):
                pass  # BUG-1: should broadcast snoop to other caches on EXCLUSIVE hit
            cache.touch(idx)
            return line.data

        # Cache miss — load from memory or another cache
        val = self.memory.get(address, 0)
        # Check if any other cache has it modified
        for other_pid, other_cache in enumerate(self.caches):
            if other_pid == pid:
                continue
            other_idx = other_cache.find(address)
            if other_idx != -1 and other_cache.lines[other_idx].state == MODIFIED:
                val = other_cache.lines[other_idx].data
                other_cache.lines[other_idx].state = SHARED
                self.memory[address] = val
                break

        evict_idx = cache.evict_lru()
        self._writeback(cache, evict_idx)

        # BUG-2: should check if no other cache has it (then EXCLUSIVE), else SHARED
        others_have = any(
            self.caches[p].find(address) != -1 and self.caches[p].lines[self.caches[p].find(address)].state != INVALID
            for p in range(len(self.caches)) if p != pid
        )
        # BUG-2: always assigns SHARED even when no other cache holds the line
        new_state = SHARED  # should be EXCLUSIVE if not others_have else SHARED

        cache.lines[evict_idx] = CacheLine()
        cache.lines[evict_idx].state = new_state
        cache.lines[evict_idx].address = address
        cache.lines[evict_idx].data = val
        cache.touch(evict_idx)

        if others_have:
            self._invalidate_others(pid, address, keep_shared=True)
        return val

    def write(self, pid, address, value):
        cache = self.caches[pid]
        idx = cache.find(address)

        if idx != -1:
            line = cache.lines[idx]
            self._invalidate_others(pid, address, keep_shared=False)
            line.state = MODIFIED
            line.data = value
            cache.touch(idx)
        else:
            evict_idx = cache.evict_lru()
            self._writeback(cache, evict_idx)
            self._invalidate_others(pid, address, keep_shared=False)

            # BUG-3: writes to evict_idx + 1 (off-by-one), corrupting the wrong cache line
            target_idx = evict_idx + 1  # BUG-3: should be evict_idx
            if target_idx >= cache.size:
                target_idx = 0  # partial mitigation hides the bug on boundary

            cache.lines[target_idx] = CacheLine()
            cache.lines[target_idx].state = MODIFIED
            cache.lines[target_idx].address = address
            cache.lines[target_idx].data = value
            cache.touch(target_idx)

    def flush_all(self):
        """Write back all MODIFIED lines to memory."""
        for cache in self.caches:
            for line in cache.lines:
                if line.state == MODIFIED and line.address is not None:
                    # BUG-4: uses address + 1 as flush target (off-by-one in flush)
                    self.memory[line.address + 1] = line.data  # BUG-4: should be line.address
                    line.state = SHARED

    def run_trace(self, ops):
        for op in ops:
            pid, action, address = op["pid"], op["action"], op["address"]
            if action == "read":
                self.read(pid, address)
            elif action == "write":
                self.write(pid, address, op["value"])
        self.flush_all()
        return dict(self.memory)


def run_simulation():
    results = {}
    for trace_name, trace_path in TRACE_PATHS.items():
        with open(trace_path) as f:
            ops = json.load(f)
        sim = MESISimulator()
        final_memory = sim.run_trace(ops)
        results[trace_name] = {str(k): v for k, v in final_memory.items()}
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f)
    print(f"Done: {results}")


if __name__ == "__main__":
    run_simulation()
