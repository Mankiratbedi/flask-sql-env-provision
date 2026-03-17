#!/bin/bash
set -euo pipefail
# CANARY-0xE8C3A2B1-counting-bloom-filter-debug

python3 - << 'PYEOF'
with open('/app/bloom_filter.py', 'r') as f:
    src = f.read()

# Fix BUG-1: _hash_positions must produce k independent positions, not XOR-collapsed one
old1 = '''        positions = []
        combined = 0  # BUG-1: accumulating XOR instead of independent positions per seed
        for seed in range(self._k):
            h = hashlib.sha256(seed.to_bytes(4, "big") + item).digest()
            val = int.from_bytes(h[:4], "big")
            combined ^= val  # BUG-1: should be positions.append(val % self._m) per seed
        positions.append(combined % self._m)  # BUG-1: all k hashes collapse to one position
        return positions'''
new1 = '''        positions = []
        for seed in range(self._k):
            h = hashlib.sha256(seed.to_bytes(4, "big") + item).digest()
            val = int.from_bytes(h[:4], "big")
            positions.append(val % self._m)
        return positions'''
assert old1 in src, "BUG-1 pattern not found"
src = src.replace(old1, new1, 1)

# Fix BUG-2: delete must guard against counter underflow and track current_count
old2 = '''        for pos in self._hash_positions(item):
            self._counters[pos] -= 1  # BUG-2: must guard against underflow: if counter > 0'''
new2 = '''        for pos in self._hash_positions(item):
            if self._counters[pos] > 0:
                self._counters[pos] -= 1
        self._current_count = max(0, self._current_count - 1)'''
assert old2 in src, "BUG-2 pattern not found"
src = src.replace(old2, new2, 1)

# Fix BUG-3: contains logic is inverted
old3 = '''        for pos in self._hash_positions(item):
            if self._counters[pos] == 0:
                return True  # BUG-3: should return False (zero means absent, not present)
        return False  # BUG-3: should return True (all positions > 0 means probably present)'''
new3 = '''        for pos in self._hash_positions(item):
            if self._counters[pos] == 0:
                return False
        return True'''
assert old3 in src, "BUG-3 pattern not found"
src = src.replace(old3, new3, 1)

# Fix BUG-4: estimate_fpr must use current_count not total count
old4 = '        n = self._count  # BUG-4: should use self._current_count (live elements, not total inserts)'
new4 = '        n = self._current_count'
assert old4 in src, "BUG-4 pattern not found"
src = src.replace(old4, new4, 1)

with open('/app/bloom_filter.py', 'w') as f:
    f.write(src)
print("All 4 bugs fixed.")
PYEOF
