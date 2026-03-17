# CANARY-0xA3F1C8D2-autograd-engine-debug
"""Scalar and tensor autograd engine with reverse-mode automatic differentiation."""
import math
import numpy as np


class Value:
    """Scalar value node supporting reverse-mode autodiff."""

    def __init__(self, data: float, _children=(), _op: str = "", label: str = ""):
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op
        self.label = label

    def __repr__(self) -> str:
        return f"Value(data={self.data:.4f}, grad={self.grad:.4f})"

    def __add__(self, other: "Value") -> "Value":
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def _backward():
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _backward
        return out

    def __radd__(self, other) -> "Value":
        return self + other

    def __neg__(self) -> "Value":
        return self * -1

    def __sub__(self, other: "Value") -> "Value":
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data - other.data, (self, other), "-")

        def _backward():
            self.grad += out.grad
            other.grad = out.grad  # BUG-1: should be -= (other.grad -= out.grad)

        out._backward = _backward
        return out

    def __rsub__(self, other) -> "Value":
        return Value(other) - self

    def __mul__(self, other: "Value") -> "Value":
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward():
            self.grad += other.data * out.grad
            other.grad = self.data * out.grad  # BUG-2: should be += (other.grad += ...)

        out._backward = _backward
        return out

    def __rmul__(self, other) -> "Value":
        return self * other

    def __truediv__(self, other: "Value") -> "Value":
        return self * other**-1

    def __rtruediv__(self, other) -> "Value":
        return Value(other) * self**-1

    def __pow__(self, other) -> "Value":
        assert isinstance(other, (int, float)), "exponent must be int or float"
        out = Value(self.data**other, (self,), f"**{other}")

        def _backward():
            self.grad += other * (self.data ** (other - 1)) * out.grad

        out._backward = _backward
        return out

    def relu(self) -> "Value":
        out = Value(max(0.0, self.data), (self,), "relu")

        def _backward():
            self.grad += (out.data >= 0) * out.grad  # BUG-3: >= includes zero, should be > 0

        out._backward = _backward
        return out

    def tanh(self) -> "Value":
        x = self.data
        t = (math.exp(2 * x) - 1) / (math.exp(2 * x) + 1)
        out = Value(t, (self,), "tanh")

        def _backward():
            self.grad += (1 - t**2) * out.grad

        out._backward = _backward
        return out

    def exp(self) -> "Value":
        out = Value(math.exp(self.data), (self,), "exp")

        def _backward():
            self.grad += out.data * out.grad

        out._backward = _backward
        return out

    def log(self) -> "Value":
        assert self.data > 0, "log of non-positive value"
        out = Value(math.log(self.data), (self,), "log")

        def _backward():
            self.grad += (1.0 / self.data) * out.grad

        out._backward = _backward
        return out

    def backward(self):
        topo = []
        visited: set = set()

        def build_topo(v: "Value"):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)
        self.grad = 1.0
        for v in reversed(topo):
            v._backward()


class Tensor:
    """2-D tensor node supporting reverse-mode autodiff."""

    def __init__(self, data, _children=(), _op: str = ""):
        self.data = np.array(data, dtype=np.float64)
        self.grad = np.zeros_like(self.data)
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op

    def __repr__(self) -> str:
        return f"Tensor(shape={self.data.shape}, op={self._op!r})"

    def __add__(self, other: "Tensor") -> "Tensor":
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data + other.data, (self, other), "+")

        def _backward():
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _backward
        return out

    def __sub__(self, other: "Tensor") -> "Tensor":
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data - other.data, (self, other), "-")

        def _backward():
            self.grad += out.grad
            other.grad -= out.grad

        out._backward = _backward
        return out

    def __mul__(self, other) -> "Tensor":
        if isinstance(other, (int, float)):
            out = Tensor(self.data * other, (self,), f"*{other}")

            def _backward():
                self.grad += other * out.grad

            out._backward = _backward
            return out
        other_t = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data * other_t.data, (self, other_t), "*")

        def _backward_elemwise():
            self.grad += other_t.data * out.grad
            other_t.grad += self.data * out.grad

        out._backward = _backward_elemwise
        return out

    def matmul(self, other: "Tensor") -> "Tensor":
        out = Tensor(self.data @ other.data, (self, other), "matmul")

        def _backward():
            self.grad += out.grad @ other.data  # BUG-4: missing .T — should be other.data.T
            other.grad += self.data.T @ out.grad

        out._backward = _backward
        return out

    def relu(self) -> "Tensor":
        out = Tensor(np.maximum(0.0, self.data), (self,), "relu")

        def _backward():
            self.grad += (self.data > 0) * out.grad

        out._backward = _backward
        return out

    def sum(self, axis=None) -> "Tensor":
        out = Tensor(np.sum(self.data, axis=axis), (self,), "sum")

        def _backward():
            if axis is None:
                self.grad += np.ones_like(self.data) * out.grad
            else:
                self.grad += np.expand_dims(out.grad, axis=axis) * np.ones_like(self.data)

        out._backward = _backward
        return out

    def mean(self) -> "Tensor":
        n = float(self.data.size)
        return self.sum() * (1.0 / n)

    def backward(self):
        topo = []
        visited: set = set()

        def build_topo(v: "Tensor"):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)
        self.grad = np.ones_like(self.data)
        for v in reversed(topo):
            v._backward()


def numerical_gradient(f, x: np.ndarray, h: float = 1e-5) -> np.ndarray:
    """Compute numerical gradient of scalar-valued f at x via central differences."""
    grad = np.zeros_like(x)
    it = np.nditer(x, flags=["multi_index"])
    while not it.finished:
        idx = it.multi_index
        old = x[idx]
        x[idx] = old + h
        fp = float(f(x))
        x[idx] = old - h
        fm = float(f(x))
        x[idx] = old
        grad[idx] = (fp - fm) / (2 * h)
        it.iternext()
    return grad
