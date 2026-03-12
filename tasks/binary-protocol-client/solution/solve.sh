#!/bin/bash
set -euo pipefail
cd /app

# Start the server in the background; it accepts one connection then exits
/app/server &
sleep 1
# Run solution client (writes /app/result.json); copy to /app/client.py so verifier can run it
python3 /solution/client.py
cp /solution/client.py /app/client.py
