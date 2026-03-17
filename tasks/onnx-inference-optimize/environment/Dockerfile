FROM python:3.13-slim

RUN apt-get update && apt-get install -y tmux && rm -rf /var/lib/apt/lists/*

# onnx==1.17.0 has no pre-built wheel for Python 3.13; only onnxruntime needed for inference
RUN pip install --no-cache-dir \
    onnxruntime==1.20.1 \
    numpy==2.2.4

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

RUN uvx \
    -p 3.13 \
    -w pytest==8.4.1 \
    -w pytest-json-ctrf==0.3.5 \
    -w numpy==2.2.4 \
    -w onnxruntime==1.20.1 \
    pytest --version

WORKDIR /app

COPY infer.py /app/infer.py
# model.onnx pre-generated with Python 3.12 + onnx==1.17.0 (seed=42, W shape 1x10)
COPY model.onnx /app/model.onnx
