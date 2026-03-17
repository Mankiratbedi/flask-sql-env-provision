# GHOST Protocol Client

A binary service is running on `localhost:9999`. You have been provided with a packet capture from a previous session: `/app/capture.pcap`.

## Your Task

Analyze the packet capture to understand the binary protocol, then write `/app/client.py` that:

1. Connects to `localhost:9999`
2. Authenticates using the GHOST protocol (the capture shows all message types and their structure)
3. Fetches the resource named `"secret"`
4. Writes the result to `/app/result.json` as:
   ```json
   {"secret": "<the secret value>"}
   ```

## Available Resources

- `/app/capture.pcap` — Packet capture of a complete GHOST protocol session
- `/app/auth_key.txt` — The authentication key used to compute the AUTH response
- The server binary `/app/ghost_server` is already running at `localhost:9999` (started by the test infrastructure)

## Inspecting the Capture

```bash
# Dump raw bytes
python3 -c "
data = open('/app/capture.pcap', 'rb').read()
print(data.hex())
"

# Or inspect specific offsets to find the protocol framing
python3 -c "
import struct
data = open('/app/capture.pcap', 'rb').read()
# Skip the 24-byte global header, then iterate pcap records (16-byte record header each)
offset = 24
while offset < len(data):
    ts_sec, ts_usec, incl_len, orig_len = struct.unpack_from('<IIII', data, offset)
    payload = data[offset+16 : offset+16+incl_len]
    print(f'offset={offset} len={incl_len} payload={payload.hex()}')
    offset += 16 + incl_len
"
```

## Protocol Notes

- Every frame starts with a 4-byte magic sequence
- The frame header encodes the message type (1 byte) and payload length (2 bytes, big-endian)
- The server sends a **fresh random nonce** each connection — you cannot replay the capture bytes directly
- The AUTH response is derived from the nonce and the key in `/app/auth_key.txt`
- Use `hmac` and `hashlib` from the Python standard library

## Output

`/app/result.json` must be valid JSON with a `"secret"` key containing the fetched secret value.
