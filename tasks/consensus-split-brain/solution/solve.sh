#!/bin/bash
set -euo pipefail

python3 - << 'PYEOF'
with open('/app/cluster.py', 'r') as f:
    src = f.read()

# Fix: restore commit_index advancement in Follower._handle_append_entries
old_bug = '''        # BUG: commit_index is never updated from leader_commit.
        # Followers accumulate log entries but never advance commit_index.
        # When a follower is promoted, commit_index stays at -1 and
        # get_committed_state() returns empty — all writes appear lost.

        self.match_index'''
new_fix = '''        with self._lock:
            if msg.leader_commit > self.commit_index:
                self.commit_index = min(msg.leader_commit, len(self.log) - 1)

        self.match_index'''

assert old_bug in src, "Could not find bug pattern in cluster.py"

fixed = src.replace(old_bug, new_fix, 1)
with open('/app/cluster.py', 'w') as f:
    f.write(fixed)
print("Bug fixed: followers now advance commit_index from leader_commit")
PYEOF

python3 /app/cluster.py
echo "Cluster test passed (exit code 0)"
