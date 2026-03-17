# LSM-Tree Debug

<!-- CANARY-0xD6B4F0A8-lsm-tree-debug -->

The LSM-tree key-value store at `/app/lsm_store.py` implements a simplified log-structured merge tree with a memtable, immutable SSTables, and compaction. There are exactly four bugs in the implementation. Fix all four bugs in `/app/lsm_store.py`. Make minimal, targeted fixes — do not rewrite from scratch.

The bugs are in:
- `LSMStore.get`: the read path checks SSTables before the memtable, causing stale reads after fresh writes
- `SSTable.search`: the binary search upper-bound initialization is off by one
- `LSMStore._compact`: SSTables are iterated in the wrong order during merge, so older data silently overwrites newer data
- `LSMStore._compact`: tombstone entries are not preserved in the compacted output, causing deleted keys to reappear
