FROM python:3.12-slim
# CANARY-0x9C1D2E3F-cache-coherence-sim

RUN apt-get update && apt-get install -y tmux && rm -rf /var/lib/apt/lists/*

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

# Install dependencies system-wide to avoid networking issues during test runs
RUN uv pip install --system pytest==8.4.1 pytest-json-ctrf==0.3.5

WORKDIR /app

COPY mesi_sim.py /app/mesi_sim.py

# Generate deterministic access traces
RUN python3 -c 'import json, os; \
    os.makedirs("/app/traces", exist_ok=True); \
    trace_a = [{"pid": 0, "action": "write", "address": 10, "value": 42}, {"pid": 1, "action": "read", "address": 10, "value": 0}, {"pid": 1, "action": "write", "address": 20, "value": 99}, {"pid": 0, "action": "read", "address": 20, "value": 0}]; \
    trace_b = [{"pid": 0, "action": "write", "address": 5, "value": 10}, {"pid": 1, "action": "write", "address": 5, "value": 20}, {"pid": 2, "action": "write", "address": 5, "value": 30}, {"pid": 0, "action": "read", "address": 5, "value": 0}, {"pid": 0, "action": "write", "address": 7, "value": 77}, {"pid": 3, "action": "read", "address": 7, "value": 0}]; \
    trace_c = [{"pid": 0, "action": "write", "address": 1, "value": 100}, {"pid": 0, "action": "write", "address": 2, "value": 200}, {"pid": 0, "action": "write", "address": 3, "value": 300}, {"pid": 0, "action": "write", "address": 4, "value": 400}, {"pid": 0, "action": "write", "address": 5, "value": 500}, {"pid": 1, "action": "read", "address": 1, "value": 0}, {"pid": 1, "action": "read", "address": 3, "value": 0}, {"pid": 2, "action": "write", "address": 2, "value": 201}]; \
    json.dump(trace_a, open("/app/traces/trace_a.json", "w")); \
    json.dump(trace_b, open("/app/traces/trace_b.json", "w")); \
    json.dump(trace_c, open("/app/traces/trace_c.json", "w")); \
    print("Traces generated")'
