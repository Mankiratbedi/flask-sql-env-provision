#!/bin/bash
set -euo pipefail
# CANARY-0xA3F1C8D2-autograd-engine-debug

python3 - << 'PYEOF'
with open('/app/autograd_engine.py', 'r') as f:
    src = f.read()

# Fix BUG-1: Value.__sub__ backward — other.grad must use -= not =
old1 = '''        def _backward():
            self.grad += out.grad
            other.grad = out.grad  # BUG-1: should be -= (other.grad -= out.grad)'''
new1 = '''        def _backward():
            self.grad += out.grad
            other.grad -= out.grad'''
assert old1 in src, "BUG-1 pattern not found"
src = src.replace(old1, new1, 1)

# Fix BUG-2: Value.__mul__ backward — other.grad must use += not =
old2 = '''        def _backward():
            self.grad += other.data * out.grad
            other.grad = self.data * out.grad  # BUG-2: should be += (other.grad += ...)'''
new2 = '''        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad'''
assert old2 in src, "BUG-2 pattern not found"
src = src.replace(old2, new2, 1)

# Fix BUG-3: Value.relu backward — >= includes zero, must use >
old3 = '''        def _backward():
            self.grad += (out.data >= 0) * out.grad  # BUG-3: >= includes zero, should be > 0'''
new3 = '''        def _backward():
            self.grad += (out.data > 0) * out.grad'''
assert old3 in src, "BUG-3 pattern not found"
src = src.replace(old3, new3, 1)

# Fix BUG-4: Tensor.matmul backward — self.grad needs other.data.T not other.data
old4 = '''        def _backward():
            self.grad += out.grad @ other.data  # BUG-4: missing .T — should be other.data.T'''
new4 = '''        def _backward():
            self.grad += out.grad @ other.data.T'''
assert old4 in src, "BUG-4 pattern not found"
src = src.replace(old4, new4, 1)

with open('/app/autograd_engine.py', 'w') as f:
    f.write(src)
print("All 4 bugs fixed.")
PYEOF
