#!/bin/bash
set -euo pipefail
# CANARY-0x9C1D2E3F-cache-coherence-sim

cd /app

python3 << 'PATCH'
with open("/app/mesi_sim.py") as f:
    src = f.read()

# Fix Bug-1: EXCLUSIVE hit should snoop/downgrade to SHARED when others may exist
src = src.replace(
    "            if line.state in (EXCLUSIVE, MODIFIED):\n                pass  # BUG-1: should broadcast snoop to other caches on EXCLUSIVE hit",
    "            if line.state == EXCLUSIVE:\n                # FIXED: downgrade to SHARED; other caches also get SHARED via snoop\n                line.state = SHARED"
)

# Fix Bug-2: always assigns SHARED — should assign EXCLUSIVE when no others hold the line
src = src.replace(
    "        # BUG-2: always assigns SHARED even when no other cache holds the line\n        new_state = SHARED  # should be EXCLUSIVE if not others_have else SHARED",
    "        # FIXED: EXCLUSIVE when sole holder, SHARED otherwise\n        new_state = SHARED if others_have else EXCLUSIVE"
)

# Fix Bug-3: off-by-one in write target index
src = src.replace(
    "            target_idx = evict_idx + 1  # BUG-3: should be evict_idx",
    "            target_idx = evict_idx  # FIXED: correct target index"
)

# Fix Bug-4: flush writes to wrong address
src = src.replace(
    "                    self.memory[line.address + 1] = line.data  # BUG-4: should be line.address",
    "                    self.memory[line.address] = line.data  # FIXED: correct address"
)

assert "BUG-" not in src, "Not all bugs were fixed!"
with open("/app/mesi_sim.py", "w") as f:
    f.write(src)
print("All four bugs fixed.")
PATCH

python3 /app/mesi_sim.py
echo "Oracle solution complete."
