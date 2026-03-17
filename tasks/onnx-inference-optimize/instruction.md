# Task: Optimize ONNX Inference Throughput

## Overview

You are given `/app/infer.py`, a Python module that runs inference against an ONNX
model (`/app/model.onnx`).  The current implementation is correct but far too slow:
it creates a brand-new `onnxruntime.InferenceSession` on **every single call** and
processes samples **one at a time**.

Your job is to optimize `infer.py` in-place so that:

1. The session is created **once** at module load time (not per call).
2. `predict(inputs)` accepts a **list** of input vectors and returns a list of
   predictions in a single batched inference call.
3. The module-level function signature stays the same: `predict(inputs: list[list[float]]) -> list[float]`.

## Requirements

1. Edit `/app/infer.py` — do **not** create additional files.
2. `predict()` must still return correct results (same values as before the optimization).
3. Throughput of 1 000 consecutive `predict([sample])` calls must reach **≥ 400 samples / second**
   when measured end-to-end (including Python call overhead).

## Expected Output

No output files are required.  The tests will import `/app/infer.py` directly and
measure correctness + throughput.

## Constraints

- Working directory: `/app`
- Do not install additional packages — `onnxruntime`, `numpy`, and `onnx` are
  already installed.
- Do not replace the model file or change the model's behaviour.
