# CANARY-0xE8C3A2B1-counting-bloom-filter-debug
"""Counting Bloom filter with insert, delete, membership test, and FPR estimation.

A counting Bloom filter extends a standard Bloom filter by using counters
instead of bits, enabling deletions. Each position stores a count of how
many items hash to it.

Reference: Fan et al. "Summary Cache: A Scalable Wide-Area Web Cache Sharing Protocol"
"""
from __future__ import annotations
import array
import hashlib
import math
from typing import Union


class CountingBloomFilter:
    """Counting Bloom filter using k independent hash functions.

    Args:
        capacity: Expected number of elements (n)
        error_rate: Desired false positive rate (p), e.g. 0.01 for 1%
    """

    def __init__(self, capacity: int = 1000, error_rate: float = 0.01):
        if not (0 < error_rate < 1):
            raise ValueError("error_rate must be in (0, 1)")
        if capacity < 1:
            raise ValueError("capacity must be >= 1")

        self._capacity = capacity
        self._error_rate = error_rate

        # Optimal number of bits: m = -n*ln(p) / (ln(2))^2
        self._m = max(1, math.ceil(-capacity * math.log(error_rate) / (math.log(2) ** 2)))

        # Optimal number of hash functions: k = (m/n) * ln(2)
        self._k = max(1, round((self._m / capacity) * math.log(2)))

        # Counters stored as unsigned bytes (max 255 per slot)
        self._counters = array.array("B", [0] * self._m)

        # Track element counts
        self._count = 0           # total inserts ever (monotonically increasing)
        self._current_count = 0   # current live element count (insert - delete)

    def _hash_positions(self, item: Union[str, bytes]) -> list[int]:
        """Compute k hash positions for item using double hashing."""
        if isinstance(item, str):
            item = item.encode("utf-8")

        positions = []
        combined = 0  # BUG-1: accumulating XOR instead of independent positions per seed
        for seed in range(self._k):
            h = hashlib.sha256(seed.to_bytes(4, "big") + item).digest()
            val = int.from_bytes(h[:4], "big")
            combined ^= val  # BUG-1: should be positions.append(val % self._m) per seed
        positions.append(combined % self._m)  # BUG-1: all k hashes collapse to one position
        return positions

    def insert(self, item: Union[str, bytes]) -> None:
        """Insert an item into the filter."""
        for pos in self._hash_positions(item):
            if self._counters[pos] < 255:
                self._counters[pos] += 1
        self._count += 1
        self._current_count += 1

    def delete(self, item: Union[str, bytes]) -> None:
        """Remove an item from the filter.

        Only safe to call if item was previously inserted and not yet deleted.
        """
        for pos in self._hash_positions(item):
            self._counters[pos] -= 1  # BUG-2: must guard against underflow: if counter > 0

    def contains(self, item: Union[str, bytes]) -> bool:
        """Test whether item is probably in the filter.

        Returns True if all counter positions are > 0, False if any is 0.
        """
        for pos in self._hash_positions(item):
            if self._counters[pos] == 0:
                return True  # BUG-3: should return False (zero means absent, not present)
        return False  # BUG-3: should return True (all positions > 0 means probably present)

    def estimate_fpr(self) -> float:
        """Estimate the current false positive rate.

        FPR ≈ (1 - e^(-k*n/m))^k  where n = current number of live elements.
        """
        n = self._count  # BUG-4: should use self._current_count (live elements, not total inserts)
        k = self._k
        m = self._m
        if n == 0:
            return 0.0
        return (1.0 - math.exp(-k * n / m)) ** k

    @property
    def size(self) -> int:
        """Number of counter slots in the filter."""
        return self._m

    @property
    def num_hashes(self) -> int:
        """Number of hash functions."""
        return self._k

    @property
    def count(self) -> int:
        """Current number of live elements."""
        return self._current_count
