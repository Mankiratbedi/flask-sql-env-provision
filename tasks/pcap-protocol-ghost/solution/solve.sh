#!/bin/bash
set -euo pipefail

# Copy reference client to /app/client.py (where tests expect it)
cp /solution/client.py /app/client.py

# Start the GHOST server in background
/app/ghost_server &
SERVER_PID=$!
sleep 0.5

# Run the client from /app
python3 /app/client.py

kill $SERVER_PID 2>/dev/null || true
