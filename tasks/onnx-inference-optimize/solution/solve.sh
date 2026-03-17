#!/bin/bash
set -euo pipefail
cd /app

python3 - <<'PY'
import re

with open("/app/infer.py") as f:
    src = f.read()

optimized = """\
#!/usr/bin/env python3
\"\"\"ONNX inference module — optimized.

Uses a module-level InferenceSession (created once) and accepts batched inputs.
\"\"\"
import numpy as np
import onnxruntime as ort

MODEL_PATH = "/app/model.onnx"

# Create the session ONCE at import time
_SESSION = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])


def predict(inputs: list) -> list:
    \"\"\"Run batched inference and return a flat list of predictions.

    Args:
        inputs: list of samples, each sample is a list of 10 floats.

    Returns:
        list of float predictions, one per input sample.
    \"\"\"
    x = np.array(inputs, dtype=np.float32)
    output = _SESSION.run(None, {"X": x})
    return [float(v) for v in output[0].flatten()]
"""

with open("/app/infer.py", "w") as f:
    f.write(optimized)

print("infer.py optimized: module-level session + batched inference")
PY
