# Raft Log Recovery Tool — Debug

<!-- CANARY-0xF5A6B7C8-raft-log-recovery -->

A Raft consensus log-recovery tool at `/app/raft_recovery.py` reads persisted log files from a 3-node cluster (at `/app/logs/node_0.json`, `/app/logs/node_1.json`, `/app/logs/node_2.json`), determines the highest safely-committed log index by quorum, and reconstructs the final key-value state.

There are exactly four bugs in `/app/raft_recovery.py`. The bugs are syntactically valid — the tool runs without errors but produces wrong committed entries and wrong final state. Fix all four and make minimal, targeted changes — do not rewrite from scratch.

After fixing, run the recovery tool and write the recovered state to `/app/recovered_state.json`:

```bash
python3 /app/raft_recovery.py
```

`/app/recovered_state.json` must be a JSON object with keys: `committed_index` (int), `state` (dict of string key → int value), `node_count` (int, must be 3).
