#!/usr/bin/env python3
"""Reference client for the binary key-value protocol. Connects to localhost:9999."""
import json
import socket
import struct

MAGIC = b"PTC0"
OP_SET = 0x01
OP_GET = 0x02
OP_RESP = 0x03
HOST = "127.0.0.1"
PORT = 9999
OUTPUT_PATH = "/app/result.json"


def send_request(sock, opcode, key, value=None):
    key_b = key.encode("utf-8")
    msg = MAGIC + bytes([opcode]) + struct.pack("!H", len(key_b)) + key_b
    if opcode == OP_SET and value is not None:
        val_b = value.encode("utf-8")
        msg += struct.pack("!H", len(val_b)) + val_b
    sock.sendall(msg)


def read_response(sock):
    buf = b""
    while len(buf) < 4:
        buf += sock.recv(4 - len(buf))
    if buf[:4] != MAGIC:
        raise ValueError("bad magic")
    buf = buf[4:]
    while len(buf) < 3:
        buf += sock.recv(3 - len(buf))
    val_len = struct.unpack("!H", buf[1:3])[0]
    buf = buf[3:]
    while len(buf) < val_len:
        buf += sock.recv(val_len - len(buf))
    return buf[:val_len]


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10.0)
        s.connect((HOST, PORT))
        send_request(s, OP_SET, "answer", "42")
        read_response(s)
        send_request(s, OP_GET, "answer")
        value_b = read_response(s)
    value = value_b.decode("utf-8")
    with open(OUTPUT_PATH, "w") as f:
        json.dump({"value": value}, f, indent=0)


if __name__ == "__main__":
    main()
