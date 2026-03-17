#!/bin/bash
set -euo pipefail

python3 - << 'PYEOF'
with open('/app/kvstore.c', 'r') as f:
    src = f.read()

old = '''            Node *dead = *pp;
            *pp = dead->next;
            /* BUG: last_accessed is NOT cleared even if it points to the freed node */
            free(dead);'''
new = '''            Node *dead = *pp;
            *pp = dead->next;
            if (last_accessed == dead) last_accessed = NULL;
            free(dead);'''

assert old in src, "Could not find bug pattern to patch"
fixed = src.replace(old, new, 1)
with open('/app/kvstore.c', 'w') as f:
    f.write(fixed)
print("Bug fixed: last_accessed cleared on node deletion")
PYEOF

gcc -O2 -o /app/kvstore_fixed /app/kvstore.c
echo "Compiled /app/kvstore_fixed"
/app/kvstore_fixed < /app/trigger.txt
