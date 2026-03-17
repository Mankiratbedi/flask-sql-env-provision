#!/usr/bin/env python3
"""Generate a synthetic PCAP showing one complete GHOST protocol session.

The PCAP uses a fixed nonce from a past session — the server generates
a fresh random nonce per connection, so replaying these bytes won't work.
The agent must understand the protocol and implement the full handshake.
"""
import struct
import hmac
import hashlib

MAGIC = bytes.fromhex('CAFEBABE')
AUTH_KEY = b'terminus-ghost-2026'
# Fixed nonce for the recorded session (the real server will send a different one)
NONCE = bytes.fromhex('a1b2c3d4e5f6001122334455667788a9')
FLAG = b'GHOST-7a3b9c2d-e5f1-4a8b-b2c3-d4e5f6a7b8c9'


def frame(opcode: int, payload: bytes = b'') -> bytes:
    return MAGIC + struct.pack('>BH', opcode, len(payload)) + payload


def build_session():
    auth_resp = hmac.new(AUTH_KEY, NONCE, hashlib.sha256).digest()[:16]
    return [
        ('c2s', frame(0x01, b'observer')),    # HELLO
        ('s2c', frame(0x02, NONCE)),           # CHALLENGE
        ('c2s', frame(0x03, auth_resp)),       # AUTH
        ('s2c', frame(0x04)),                  # AUTH_OK
        ('c2s', frame(0x10, b'secret')),       # FETCH secret
        ('s2c', frame(0x11, FLAG)),            # FETCH_RESP
    ]


try:
    from scapy.all import Ether, IP, TCP, Raw, wrpcap

    SERVER_IP = '10.0.0.1'
    CLIENT_IP = '10.0.0.2'
    SERVER_PORT = 9999
    CLIENT_PORT = 54321

    pkts = []
    seq_c, seq_s = 1000, 2000

    # TCP 3-way handshake
    pkts.append(Ether() / IP(src=CLIENT_IP, dst=SERVER_IP) /
                TCP(sport=CLIENT_PORT, dport=SERVER_PORT, flags='S', seq=seq_c))
    seq_c += 1
    pkts.append(Ether() / IP(src=SERVER_IP, dst=CLIENT_IP) /
                TCP(sport=SERVER_PORT, dport=CLIENT_PORT, flags='SA', seq=seq_s, ack=seq_c))
    seq_s += 1
    pkts.append(Ether() / IP(src=CLIENT_IP, dst=SERVER_IP) /
                TCP(sport=CLIENT_PORT, dport=SERVER_PORT, flags='A', seq=seq_c, ack=seq_s))

    for direction, data in build_session():
        if direction == 'c2s':
            p = (Ether() / IP(src=CLIENT_IP, dst=SERVER_IP) /
                 TCP(sport=CLIENT_PORT, dport=SERVER_PORT, flags='PA', seq=seq_c, ack=seq_s) /
                 Raw(load=data))
            seq_c += len(data)
            pkts.append(p)
            pkts.append(Ether() / IP(src=SERVER_IP, dst=CLIENT_IP) /
                        TCP(sport=SERVER_PORT, dport=CLIENT_PORT, flags='A', seq=seq_s, ack=seq_c))
        else:
            p = (Ether() / IP(src=SERVER_IP, dst=CLIENT_IP) /
                 TCP(sport=SERVER_PORT, dport=CLIENT_PORT, flags='PA', seq=seq_s, ack=seq_c) /
                 Raw(load=data))
            seq_s += len(data)
            pkts.append(p)
            pkts.append(Ether() / IP(src=CLIENT_IP, dst=SERVER_IP) /
                        TCP(sport=CLIENT_PORT, dport=SERVER_PORT, flags='A', seq=seq_c, ack=seq_s))

    # FIN
    pkts.append(Ether() / IP(src=CLIENT_IP, dst=SERVER_IP) /
                TCP(sport=CLIENT_PORT, dport=SERVER_PORT, flags='FA', seq=seq_c, ack=seq_s))

    wrpcap('/app/capture.pcap', pkts)
    print("Generated /app/capture.pcap using scapy")

except ImportError:
    # Fallback: write a minimal valid pcap manually (linktype=RAW/101 for simplicity)
    import struct as _s
    import time

    def pcap_global_header():
        # magic, version maj/min, thiszone, sigfigs, snaplen, network(RAW=101)
        return _s.pack('<IHHiIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 101)

    def pcap_packet(data):
        ts = int(time.time())
        return _s.pack('<IIII', ts, 0, len(data), len(data)) + data

    with open('/app/capture.pcap', 'wb') as f:
        f.write(pcap_global_header())
        for direction, data in build_session():
            f.write(pcap_packet(data))
    print("Generated /app/capture.pcap (raw payload fallback)")
