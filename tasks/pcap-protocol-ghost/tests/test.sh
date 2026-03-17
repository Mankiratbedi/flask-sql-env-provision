#!/bin/bash
export PATH="/usr/local/bin:$HOME/.local/bin:$PATH"

# Start the GHOST server in background
/app/ghost_server &
SERVER_PID=$!
sleep 0.5

# Run the agent's client
python3 /app/client.py 2>/dev/null || true

# Stop the server
kill $SERVER_PID 2>/dev/null || true


uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA || true

python3 -c "
import json
try:
    with open('/logs/verifier/ctrf.json') as f:
        data = json.load(f)
    summary = data.get('results', {}).get('summary', {})
    total = summary.get('tests', 0)
    passed = summary.get('passed', 0)
    reward = passed / total if total > 0 else 0.0
    with open('/logs/verifier/reward.json', 'w') as f:
        json.dump({'reward': reward}, f)
except Exception:
    with open('/logs/verifier/reward.json', 'w') as f:
        json.dump({'reward': 0.0}, f)
"
