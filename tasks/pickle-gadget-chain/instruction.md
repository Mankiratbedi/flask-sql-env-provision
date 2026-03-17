# Pickle Gadget Chain

A Python service (`/app/service.py`) deserializes user-provided pickle data using a `SafeUnpickler` that restricts which classes can be instantiated. Your goal is to exploit a vulnerability in the service to achieve code execution.

## The Service

```bash
python3 /app/service.py < payload.pkl
```

The service:
1. Reads a pickle payload from stdin
2. Deserializes it using `SafeUnpickler` (which blocks most classes via `find_class`)
3. Calls `persist()` to save the result

## Your Task

Find the vulnerability in the service and craft an exploit that writes the string `pwned` to `/app/pwned.txt`.

1. Analyze `/app/service.py` to identify the vulnerability
2. Write `/app/exploit.py` that generates a pickle payload and saves it to `/app/exploit.pkl`
3. The exploit chain must cause `/app/pwned.txt` to contain `pwned` after running:
   ```bash
   python3 /app/exploit.py
   python3 /app/service.py < /app/exploit.pkl
   ```

## Deliverables

- `/app/exploit.py` — generates the exploit payload
- `/app/exploit.pkl` — the pickle payload (produced by running `exploit.py`)
- `/app/pwned.txt` — proof of code execution (content: `pwned`)

## Hint

The `SafeUnpickler` blocks class instantiation via `find_class`. Read the full service code — is `find_class` the only place where user-controlled data is processed unsafely?
