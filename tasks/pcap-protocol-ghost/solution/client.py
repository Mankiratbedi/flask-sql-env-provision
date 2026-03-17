#!/usr/bin/env python3
"""Reference client for the GHOST protocol."""
import socket
import struct
import hmac
import hashlib
import json

MAGIC = bytes.fromhex('CAFEBABE')

OP_HELLO = 0x01
OP_CHALLENGE = 0x02
OP_AUTH = 0x03
OP_AUTH_OK = 0x04
OP_FETCH = 0x10
OP_FETCH_RESP = 0x11


def send_frame(s, opcode, payload=b''):
    msg = MAGIC + struct.pack('>BH', opcode, len(payload)) + payload
    s.sendall(msg)


def recv_frame(s):
    magic = b''
    while len(magic) < 4:
        chunk = s.recv(4 - len(magic))
        if not chunk:
            raise ConnectionError("connection closed reading magic")
        magic += chunk
    assert magic == MAGIC, f"bad magic: {magic.hex()}"
    hdr = b''
    while len(hdr) < 3:
        chunk = s.recv(3 - len(hdr))
        if not chunk:
            raise ConnectionError("connection closed reading header")
        hdr += chunk
    opcode, plen = struct.unpack('>BH', hdr)
    payload = b''
    while len(payload) < plen:
        chunk = s.recv(plen - len(payload))
        if not chunk:
            raise ConnectionError("connection closed reading payload")
        payload += chunk
    return opcode, payload


def main():
    with open('/app/auth_key.txt', 'rb') as f:
        key = f.read().strip()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 9999))

    # HELLO
    send_frame(s, OP_HELLO, b'agent')

    # Receive CHALLENGE
    opcode, nonce = recv_frame(s)
    assert opcode == OP_CHALLENGE, f"expected CHALLENGE (0x02), got {opcode:#x}"

    # AUTH: HMAC-SHA256(key, nonce)[:16]
    auth_resp = hmac.new(key, nonce, hashlib.sha256).digest()[:16]
    send_frame(s, OP_AUTH, auth_resp)

    # AUTH_OK
    opcode, _ = recv_frame(s)
    assert opcode == OP_AUTH_OK, f"expected AUTH_OK (0x04), got {opcode:#x}"

    # FETCH secret
    send_frame(s, OP_FETCH, b'secret')

    # FETCH_RESP
    opcode, value = recv_frame(s)
    assert opcode == OP_FETCH_RESP, f"expected FETCH_RESP (0x11), got {opcode:#x}"

    with open('/app/result.json', 'w') as f:
        json.dump({'secret': value.decode('utf-8')}, f)

    s.close()
    print(f"Fetched: {value.decode()}")


if __name__ == '__main__':
    main()
