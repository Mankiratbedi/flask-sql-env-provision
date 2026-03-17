FROM python:3.12-slim
# CANARY-0x4A2F8E91-jit-trace-deopt-debug

RUN apt-get update && apt-get install -y tmux && rm -rf /var/lib/apt/lists/*

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

# Install dependencies system-wide to avoid networking issues during test runs
RUN uv pip install --system pytest==8.4.1 pytest-json-ctrf==0.3.5

WORKDIR /app

COPY batch_stats.py /app/batch_stats.py

# Generate a deterministic dataset for the pipeline
RUN python3 -c 'import json, math, random; \
    random.seed(42); \
    values = [round(random.uniform(10.5, 99.5), 2) for _ in range(175)]; \
    json.dump({"values": values}, open("/app/dataset.json", "w")); \
    print("Dataset generated:", len(values), "values")'
