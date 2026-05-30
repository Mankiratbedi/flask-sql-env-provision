#!/bin/bash
set -euo pipefail

# 1. Apply Milestone 1 patches to provision.py
python3 -c '
with open("/app/provision.py", "r") as f:
    content = f.read()
old_line = "subprocess.run([pip_path, \"install\", \"-r\", req_path], check=True)"
new_line = "subprocess.run([pip_path, \"install\", \"--no-index\", \"--find-links=/opt/wheels\", \"-r\", req_path], check=True)"
content = content.replace(old_line, new_line)
with open("/app/provision.py", "w") as f:
    f.write(content)
'

chmod +x /app/provision.py
/app/provision.py bootstrap

# 2. Correct schema.sql to fix syntax, add UNIQUE constraint, and make it idempotent (IF NOT EXISTS)
cat << 'EOF' > /app/api/schema.sql
-- SQLite Database Schema for Assets
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    quantity INTEGER DEFAULT 0
);
EOF

# 3. Execute db-init
/app/provision.py db-init
