#!/bin/bash
set -euo pipefail
# CANARY-0x7B3C4D5E-merkle-audit-tamper

cd /app

python3 << 'PATCH'
with open("/app/merkle_log.py") as f:
    src = f.read()

# Fix Bug-1: missing domain separator prefix for leaf hash
src = src.replace(
    "    # BUG-1: missing b'\\x01' prefix — should be hashlib.sha256(b'\\x01' + data).digest()\n    return hashlib.sha256(data).digest()",
    "    # FIXED: domain-separated leaf hash\n    return hashlib.sha256(b'\\x01' + data).digest()"
)

# Fix Bug-2: reversed concatenation order in internal_hash
src = src.replace(
    "    # BUG-2: operands reversed — should be sha256(b'\\x00' + left + right).digest()\n    return hashlib.sha256(b\"\\x00\" + right + left).digest()",
    "    # FIXED: correct concatenation order\n    return hashlib.sha256(b\"\\x00\" + left + right).digest()"
)

# Fix Bug-3: proof verify — 'right' case args swapped
src = src.replace(
    "            # BUG-3: args swapped — should be internal_hash(current, sibling)\n            current = internal_hash(sibling, current)",
    "            # FIXED: correct order for right sibling\n            current = internal_hash(current, sibling)"
)

# Fix Bug-4: proof verify — 'left' case args swapped
src = src.replace(
    "            # BUG-4: args swapped — should be internal_hash(sibling, current)\n            current = internal_hash(current, sibling)",
    "            # FIXED: correct order for left sibling\n            current = internal_hash(sibling, current)"
)

assert "BUG-" not in src, "Not all bugs were fixed!"
with open("/app/merkle_log.py", "w") as f:
    f.write(src)
print("All four bugs fixed.")
PATCH

python3 /app/merkle_log.py
echo "Oracle solution complete."
