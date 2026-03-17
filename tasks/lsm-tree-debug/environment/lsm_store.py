# CANARY-0xD6B4F0A8-lsm-tree-debug
"""Simplified LSM-tree (Log-Structured Merge Tree) key-value store.

Architecture:
  - Memtable: in-memory sorted dict (newest writes, including tombstones)
  - SSTables: list of immutable sorted tables flushed from memtable
              newer SSTables have higher sequence numbers
  - Compaction: merges all SSTables into one, resolving conflicts by taking
                the entry from the SSTable with the highest sequence number
  - Tombstone: a deletion marker stored as value=None; any key with a
               tombstone in the most-recent position is considered deleted
"""
from __future__ import annotations
from typing import Any, Optional


_TOMBSTONE = object()   # sentinel for deleted keys in memtable


class SSTableEntry:
    """One key-value entry in an SSTable."""
    __slots__ = ("key", "value", "seq")

    def __init__(self, key: str, value: Any, seq: int):
        self.key = key
        self.value = value   # None means tombstone
        self.seq = seq

    def __repr__(self) -> str:
        return f"Entry({self.key!r}, {self.value!r}, seq={self.seq})"


class SSTable:
    """Immutable sorted table of key-value entries."""

    def __init__(self, entries: list[SSTableEntry], seq: int):
        self.entries = sorted(entries, key=lambda e: e.key)
        self.seq = seq

    def search(self, key: str) -> Optional[SSTableEntry]:
        """Binary search for key. Returns entry or None if not found."""
        lo, hi = 0, len(self.entries) - 2  # BUG-2: should be len(self.entries) - 1 (last element excluded)
        while lo <= hi:
            mid = (lo + hi) // 2
            entry = self.entries[mid]
            if entry.key == key:
                return entry
            elif entry.key < key:
                lo = mid + 1
            else:
                hi = mid - 1
        return None

    def __repr__(self) -> str:
        return f"SSTable(seq={self.seq}, n={len(self.entries)})"


class LSMStore:
    """LSM-tree key-value store with memtable + SSTable layers."""

    def __init__(self, memtable_limit: int = 8):
        self._memtable: dict[str, Any] = {}
        self._sstables: list[SSTable] = []
        self._seq = 0
        self._memtable_limit = memtable_limit

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def put(self, key: str, value: Any) -> None:
        """Insert or update a key."""
        self._memtable[key] = value
        if len(self._memtable) >= self._memtable_limit:
            self._flush()

    def delete(self, key: str) -> None:
        """Delete a key by writing a tombstone."""
        self._memtable[key] = _TOMBSTONE
        if len(self._memtable) >= self._memtable_limit:
            self._flush()

    def get(self, key: str) -> Optional[Any]:
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

        return None

    def _flush(self) -> None:
        """Flush memtable to a new SSTable."""
        entries = []
        seq = self._next_seq()
        for k, v in self._memtable.items():
            tombstone_value = None if v is _TOMBSTONE else v
            entries.append(SSTableEntry(k, tombstone_value, seq))
        self._sstables.append(SSTable(entries, seq))
        self._memtable.clear()

    def _compact(self) -> None:
        """Merge all SSTables into a single new SSTable (major compaction).

        Conflict resolution: the entry from the SSTable with the HIGHEST
        sequence number wins (newest data takes priority).
        Tombstones are preserved so that deleted keys stay deleted.
        """
        if len(self._sstables) < 2:
            return

        merged: dict[str, SSTableEntry] = {}

        for sstable in self._sstables:  # BUG-3: should be reversed(); ascending order lets old data overwrite new
            for entry in sstable.entries:
                if entry.key not in merged or sstable.seq > merged[entry.key].seq:
                    merged[entry.key] = entry

        compacted_entries = []
        for key, entry in sorted(merged.items()):
            if entry.value is not None:  # BUG-4: tombstones must be preserved; remove this guard
                compacted_entries.append(entry)

        new_seq = self._next_seq()
        new_table = SSTable(compacted_entries, new_seq)
        self._sstables = [new_table]

    def flush_and_compact(self) -> None:
        """Flush memtable then compact all SSTables."""
        if self._memtable:
            self._flush()
        self._compact()

    def scan(self, start: str = "", end: str = "\xff\xff") -> list[tuple[str, Any]]:
        """Return all live key-value pairs in [start, end] range, sorted by key."""
        all_keys: set[str] = set(self._memtable.keys())
        for sst in self._sstables:
            for entry in sst.entries:
                all_keys.add(entry.key)

        result = []
        for key in sorted(all_keys):
            if start <= key <= end:
                val = self.get(key)
                if val is not None:
                    result.append((key, val))
        return result
