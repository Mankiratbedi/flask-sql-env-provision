# Reverse-Engineer Binary Protocol and Implement Client

## Overview

You are given a packet capture of an unknown binary protocol. There is **no specification or source code**. You must infer the protocol from the capture, implement a client that speaks it, perform a specific sequence of operations, and write the result to a JSON file.

**Your only source of information about the protocol is the packet capture.** A server binary is present in the environment for the verifier to run; you must **not** use or reverse-engineer the server binary. Use only `/app/capture.pcap` to infer message format, opcodes, and encoding.

## Environment

- Packet capture: `/app/capture.pcap`
- Working directory: `/app`
- The server (when run by the verifier) listens on **localhost, port 9999**

## Task

1. **Analyze** `/app/capture.pcap` to determine:
   - Message boundaries and structure
   - Request and response formats
   - How keys and values are encoded (lengths, byte order, etc.)

2. **Implement a client** at `/app/client.py` that:
   - Connects to the server at `localhost:9999`
   - Performs the following sequence in order:
     - **SET** key `"answer"` to value `"42"`
     - **GET** key `"answer"`
   - Writes the result of the GET to the output file (see below)

3. **Output:** Your client must be runnable as:
   ```bash
   python3 /app/client.py
   ```
   The verifier will start the server and run this command. Your client must write its result to:

   **Path:** `/app/result.json`

   **Schema (exact):**
   ```json
   {
     "value": "<string>"
   }
   ```
   where `"value"` is the string returned by the GET operation (the value previously set for key `"answer"`). For the required sequence, this must be `"42"`.

## Requirements Summary

- Use **only** `/app/capture.pcap` to infer the protocol; do not use the server binary.
- Implement the client at `/app/client.py`, runnable as `python3 /app/client.py`.
- Client must connect to `localhost:9999`, perform SET `"answer"` → `"42"`, then GET `"answer"`.
- Write the GET result to `/app/result.json` with the exact schema above (`"value"` key, string value).

## Constraints

- All work must be done locally; no external services or internet.
- Output file path must be exactly `/app/result.json`.
