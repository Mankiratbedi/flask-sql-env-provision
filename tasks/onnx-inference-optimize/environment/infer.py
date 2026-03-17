#!/usr/bin/env python3
"""ONNX inference module.

Runs a linear regression model stored at /app/model.onnx.

BUG: A new InferenceSession is created on every predict() call,
and samples are processed one at a time.  Both are unnecessary and slow.
"""
import numpy as np
import onnxruntime as ort

MODEL_PATH = "/app/model.onnx"


def predict(inputs: list) -> list:
    """Run inference and return a flat list of predictions.

    Args:
        inputs: list of samples, each sample is a list of 10 floats.

    Returns:
        list of float predictions, one per input sample.
    """
    results = []
    for sample in inputs:
        # BUG: new session per sample — extremely expensive
        session = ort.InferenceSession(MODEL_PATH,
                                       providers=["CPUExecutionProvider"])
        x = np.array([sample], dtype=np.float32)
        output = session.run(None, {"X": x})
        results.append(float(output[0][0][0]))
    return results
