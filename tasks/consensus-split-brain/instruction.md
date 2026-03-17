# Consensus Split-Brain

A distributed log-replication system is losing committed writes after leader failover.

## Setup

`/app/cluster.py` implements a simplified 3-node leader-based log replication protocol:
- One **Leader** accepts client writes
- Two **Followers** replicate the leader's log
- A write is "committed" when acknowledged by a majority (≥ 2/3 nodes)
- On leader failure, a follower is promoted to leader and serves reads from its committed state

## The Bug

The system has a correctness bug: writes that appear to succeed are sometimes lost after leader failover. Run the built-in test to see it:

```bash
python3 /app/cluster.py
# exits with code 1 and prints DATA LOSS messages
```

## Your Task

1. Read `/app/cluster.py` carefully
2. Identify the bug that causes data loss on leader failover
3. Fix the bug in `/app/cluster.py`
4. Verify your fix:
   ```bash
   python3 /app/cluster.py
   # must exit with code 0 (no data loss)
   ```

## Hint

Think carefully about the ordering of operations in `_handle_client_write`. A write is only truly committed when a majority of nodes confirm they have it — not when the leader appends it to its own log.

## Deliverable

Fixed `/app/cluster.py` that exits with code `0` when run as a script.
