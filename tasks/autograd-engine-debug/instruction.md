# Autograd Engine Debug

<!-- CANARY-0xA3F1C8D2-autograd-engine-debug -->

The autograd engine at `/app/autograd_engine.py` implements scalar (`Value`) and 2-D tensor (`Tensor`) nodes for reverse-mode automatic differentiation. There are exactly four bugs in the backward pass implementations. Fix all four bugs in `/app/autograd_engine.py`. Make minimal, targeted fixes — do not rewrite from scratch.

The bugs are in:
- `Value.__sub__` backward: gradient for the second operand is computed incorrectly
- `Value.__mul__` backward: gradient accumulation for the second operand is broken
- `Value.relu` backward: boundary condition on the gate is off by one comparison
- `Tensor.matmul` backward: missing matrix transposition for the first operand's gradient
