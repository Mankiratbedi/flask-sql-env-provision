# Counting Bloom Filter Debug

<!-- CANARY-0xE8C3A2B1-counting-bloom-filter-debug -->

The counting Bloom filter implementation at `/app/bloom_filter.py` supports insert, delete, membership testing, and false positive rate estimation. There are exactly four bugs in the implementation. Fix all four bugs in `/app/bloom_filter.py`. Make minimal, targeted fixes — do not rewrite from scratch.

The bugs are in:
- `_hash_positions`: all k hash functions collapse to a single position via XOR instead of producing k independent positions
- `delete`: decrements counters without checking for zero, causing unsigned byte underflow
- `contains`: the return values are inverted — zero counter indicates absence, not presence
- `estimate_fpr`: uses total insert count (including deleted items) instead of current live element count
