#!/bin/bash
set -euo pipefail
# CANARY-0xD6B4F0A8-lsm-tree-debug

python3 - << 'PYEOF'
with open('/app/lsm_store.py', 'r') as f:
    src = f.read()

# Fix BUG-1: get() must check memtable first (it has most recent writes)
old1 = '''    def get(self, key: str) -> Optional[Any]:
        """Retrieve the most recent value for key, or None if deleted/not found."""
        # BUG-1: SSTables checked before memtable; memtable has most recent writes
        for sstable in reversed(self._sstables):
            entry = sstable.search(key)
            if entry is not None:
                return None if entry.value is None else entry.value

        if key in self._memtable:
            v = self._memtable[key]
            if v is _TOMBSTONE:
                return None
            return v

        return None'''
new1 = '''    def get(self, key: str) -> Optional[Any]:
        """Retrieve the most recent value for key, or None if deleted/not found."""
        if key in self._memtable:
            v = self._memtable[key]
            if v is _TOMBSTONE:
                return None
            return v

        for sstable in reversed(self._sstables):
            entry = sstable.search(key)
            if entry is not None:
                return None if entry.value is None else entry.value

        return None'''
assert old1 in src, "BUG-1 pattern not found"
src = src.replace(old1, new1, 1)

# Fix BUG-2: binary search hi must be len-1 not len-2
old2 = '        lo, hi = 0, len(self.entries) - 2  # BUG-2: should be len(self.entries) - 1 (last element excluded)'
new2 = '        lo, hi = 0, len(self.entries) - 1'
assert old2 in src, "BUG-2 pattern not found"
src = src.replace(old2, new2, 1)

# Fix BUG-3: must iterate reversed so newest SSTable wins
old3 = '        for sstable in self._sstables:  # BUG-3: should be reversed(); ascending order lets old data overwrite new'
new3 = '        for sstable in reversed(self._sstables):'
assert old3 in src, "BUG-3 pattern not found"
src = src.replace(old3, new3, 1)

# Fix BUG-4: remove guard that drops tombstones during compaction
old4 = '''        compacted_entries = []
        for key, entry in sorted(merged.items()):
            if entry.value is not None:  # BUG-4: tombstones must be preserved; remove this guard
                compacted_entries.append(entry)'''
new4 = '''        compacted_entries = []
        for key, entry in sorted(merged.items()):
            compacted_entries.append(entry)'''
assert old4 in src, "BUG-4 pattern not found"
src = src.replace(old4, new4, 1)

with open('/app/lsm_store.py', 'w') as f:
    f.write(src)
print("All 4 bugs fixed.")
PYEOF
