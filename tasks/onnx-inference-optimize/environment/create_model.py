#!/usr/bin/env python3
"""Create a simple ONNX linear model for the optimization task.

Model: y = W @ x + b  (10-dimensional input → 1-dimensional output)
Weights are fixed/deterministic so tests are reproducible.
"""
import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper

np.random.seed(42)
W = np.random.randn(1, 10).astype(np.float32)
b = np.random.randn(1).astype(np.float32)

# Build the ONNX graph
X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [None, 10])
Y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [None, 1])

W_init = numpy_helper.from_array(W, name="W")
b_init = numpy_helper.from_array(b, name="b")

gemm = helper.make_node("Gemm", inputs=["X", "W", "b"], outputs=["Y"],
                         transB=1)

graph = helper.make_graph([gemm], "linear", [X], [Y],
                           initializer=[W_init, b_init])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
onnx.checker.check_model(model)
onnx.save(model, "/app/model.onnx")
print("Saved /app/model.onnx")
