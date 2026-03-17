# Merkle Audit Log — Verification Bug

<!-- CANARY-0x7B3C4D5E-merkle-audit-tamper -->

An append-only Merkle audit-log library at `/app/merkle_log.py` is used to detect tampering in a SQLite database at `/app/audit.db`. The library builds a Merkle tree over log entries and provides root computation and inclusion-proof verification.

There are exactly four bugs in `/app/merkle_log.py`. The bugs are syntactically valid — the code runs without errors but computes wrong Merkle roots and produces invalid proofs. Fix all four and make minimal, targeted changes — do not rewrite from scratch.

After fixing, run the verifier and write results to `/app/result.json`:

```bash
python3 /app/merkle_log.py
```

`/app/result.json` must be a JSON object with keys: `root` (hex string, 64 chars), `entry_count` (int), `proofs_valid` (bool). `proofs_valid` must be `true` — meaning all generated inclusion proofs verify correctly against the computed root.
