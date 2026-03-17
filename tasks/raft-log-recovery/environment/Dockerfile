FROM python:3.12-slim
# CANARY-0xF5A6B7C8-raft-log-recovery

RUN apt-get update && apt-get install -y tmux && rm -rf /var/lib/apt/lists/*

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

# Install dependencies system-wide to avoid networking issues during test runs
RUN uv pip install --system pytest==8.4.1 pytest-json-ctrf==0.3.5

WORKDIR /app

COPY raft_recovery.py /app/raft_recovery.py

# Generate 3-node Raft log files
RUN python3 -c 'import json, os; \
    os.makedirs("/app/logs", exist_ok=True); \
    node_0 = {"node_id": 0, "current_term": 3, "snapshot": {"x": 999, "initial_flag": 1}, "log": [{"term": 2, "index": 0, "command": {"op": "set", "key": "x", "value": 1}}, {"term": 2, "index": 1, "command": {"op": "set", "key": "y", "value": 2}}, {"term": 3, "index": 2, "command": {"op": "set", "key": "x", "value": 10}}, {"term": 3, "index": 3, "command": {"op": "set", "key": "z", "value": 99}}]}; \
    node_1 = {"node_id": 1, "current_term": 3, "snapshot": {}, "log": [{"term": 2, "index": 0, "command": {"op": "set", "key": "x", "value": 1}}, {"term": 2, "index": 1, "command": {"op": "set", "key": "y", "value": 2}}, {"term": 3, "index": 2, "command": {"op": "set", "key": "x", "value": 10}}]}; \
    node_2 = {"node_id": 2, "current_term": 2, "snapshot": {}, "log": [{"term": 2, "index": 0, "command": {"op": "set", "key": "x", "value": 100}}]}; \
    json.dump(node_0, open("/app/logs/node_0.json", "w")); \
    json.dump(node_1, open("/app/logs/node_1.json", "w")); \
    json.dump(node_2, open("/app/logs/node_2.json", "w")); \
    print("Raft logs generated")'
