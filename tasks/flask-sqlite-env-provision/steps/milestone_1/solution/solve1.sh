#!/bin/bash
set -euo pipefail

# Patch provision.py to use local offline wheels for package installation
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
