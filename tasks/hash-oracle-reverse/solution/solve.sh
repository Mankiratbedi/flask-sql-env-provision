#!/bin/bash
set -euo pipefail

cat > /app/myhash.py << 'PYEOF'
"""Reverse-engineered implementation of the custom_hash function."""


def custom_hash(data: bytes) -> int:
    """Custom 32-bit hash: rotate-XOR-multiply chain with final avalanche.

    Init: h = 0xDEADBEEF
    Per byte: h ^= byte; h = rotl32(h, 7); h *= 0x45D9F3B
    Final: h ^= (h >> 16)
    """
    h = 0xDEADBEEF
    for b in data:
        h ^= b
        h = ((h << 7) | (h >> 25)) & 0xFFFFFFFF
        h = (h * 0x45D9F3B) & 0xFFFFFFFF
    h ^= (h >> 16)
    return h & 0xFFFFFFFF
PYEOF

echo "Written /app/myhash.py"
python3 -c "
import sys
sys.path.insert(0, '/app')
from myhash import custom_hash
print('empty:', custom_hash(b''))
print('deadbeef:', custom_hash(bytes.fromhex('deadbeef')))
"
