#!/bin/bash
set -euo pipefail
# CANARY-0xB7E2D491-recursive-descent-parser-debug

python3 - << 'PYEOF'
with open('/app/expr_parser.py', 'r') as f:
    src = f.read()

# Fix BUG-1: parse_term must call parse_power(), not parse_expr()
old1 = '            right = self.parse_expr()  # BUG-1: should call parse_power(), not parse_expr()'
new1 = '            right = self.parse_power()'
assert old1 in src, "BUG-1 pattern not found"
src = src.replace(old1, new1, 1)

# Fix BUG-2: parse_unary must recurse into parse_unary(), not parse_primary()
old2 = '            return -self.parse_primary()  # BUG-2: should call parse_unary() not parse_primary()'
new2 = '            return -self.parse_unary()'
assert old2 in src, "BUG-2 pattern not found"
src = src.replace(old2, new2, 1)

with open('/app/expr_parser.py', 'w') as f:
    f.write(src)
print("Both bugs fixed.")
PYEOF
