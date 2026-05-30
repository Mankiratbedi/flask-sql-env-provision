#!/bin/bash
set -euo pipefail

# Clean up any existing Flask processes to prevent port conflicts
if [ -f /app/run/flask.pid ]; then
    kill "$(cat /app/run/flask.pid)" 2>/dev/null || true
    rm -f /app/run/flask.pid
fi

# 1. Apply all CLI patches for Milestone 1, 2, and 3
python3 -c '
with open("/app/provision.py", "r") as f:
    content = f.read()

# Pip install offline
old_pip = "subprocess.run([pip_path, \"install\", \"-r\", req_path], check=True)"
new_pip = "subprocess.run([pip_path, \"install\", \"--no-index\", \"--find-links=/opt/wheels\", \"-r\", req_path], check=True)"
content = content.replace(old_pip, new_pip)

# Secure key
old_key = "weak_key = f\"key_{random.random()}\""
new_key = "import secrets\n        weak_key = secrets.token_hex(32)"
content = content.replace(old_key, new_key)

# Health check retry loop
old_health = """    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            if res_data.get("status") == "healthy":
                print("Service health check: PASS")
            else:
                print("Service health check: FAIL (Status unhealthy)")
                sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Service health check failed: {e}", file=sys.stderr)
        sys.exit(1)"""

new_health = """    for attempt in range(10):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode())
                if res_data.get("status") == "healthy":
                    print("Service health check: PASS")
                    break
                else:
                    print("Service health check: FAIL (Status unhealthy)")
                    sys.exit(1)
        except urllib.error.URLError as e:
            if attempt == 9:
                print(f"Service health check failed after retries: {e}", file=sys.stderr)
                sys.exit(1)
            time.sleep(1)"""

content = content.replace(old_health, new_health)

# Correct credentials
old_auth = "payload = json.dumps({\"username\": \"admin\", \"password\": \"wrong-password\"}).encode(\"utf-8\")"
new_auth = "payload = json.dumps({\"username\": \"admin\", \"password\": \"secret-provision-password\"}).encode(\"utf-8\")"
content = content.replace(old_auth, new_auth)

with open("/app/provision.py", "w") as f:
    f.write(content)
'

chmod +x /app/provision.py

# 2. Correct schema.sql
cat << 'EOF' > /app/api/schema.sql
-- SQLite Database Schema for Assets
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    quantity INTEGER DEFAULT 0
);
EOF

# 3. Boot environment
/app/provision.py bootstrap
/app/provision.py db-init
/app/provision.py start --port 5000
/app/provision.py check --port 5000
