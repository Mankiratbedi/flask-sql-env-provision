#!/usr/bin/env python3
"""Generate capture.pcap with TCP packets containing the binary protocol messages.

Run once on the host: python3 gen_capture.py
Output: capture.pcap in the same directory.

Protocol: magic "PTC0", opcode (1), key_len (2 BE), key; for SET: value_len (2 BE), value.
Response: magic "PTC0", 0x03, value_len (2 BE), value.
"""
import os
import socket
import struct


def build_ipv4_packet(src_ip: str, dst_ip: str, protocol: int, payload: bytes) -> bytes:
    """Build minimal IPv4 header + payload."""
    total_length = 20 + len(payload)
    header = struct.pack(
        "!BBHHHBBH4s4s",
        0x45, 0, total_length, 0, 0x4000, 64, protocol, 0,
        socket.inet_aton(src_ip), socket.inet_aton(dst_ip),
    )
    words = struct.unpack("!10H", header)
    s = sum(words)
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    checksum = ~s & 0xFFFF
    header = struct.pack(
        "!BBHHHBBH4s4s",
        0x45, 0, total_length, 0, 0x4000, 64, protocol, checksum,
        socket.inet_aton(src_ip), socket.inet_aton(dst_ip),
    )
    return header + payload


def build_tcp_packet(
    src_port: int, dst_port: int, seq: int, ack: int, payload: bytes, flags: int = 0x18
) -> bytes:
    """Build minimal TCP header (20 bytes) + payload. Checksum 0 for simplicity."""
    offset_flags = (5 << 12) | flags  # data offset 5, flags
    header = struct.pack(
        "!HHIIHHHH",
        src_port, dst_port, seq, ack, offset_flags, 65535, 0, 0,
    )
    return header + payload


def build_ethernet_frame(payload: bytes) -> bytes:
    """Ethernet II frame."""
    dst_mac = b"\x00\x1a\x2b\x3c\x4d\x5e"
    src_mac = b"\x00\x5e\x4d\x3c\x2b\x1a"
    ethertype = struct.pack("!H", 0x0800)
    return dst_mac + src_mac + ethertype + payload


def write_pcap(filename: str, packets: list[tuple[float, bytes]]) -> None:
    """Write packets to a PCAP file."""
    with open(filename, "wb") as f:
        f.write(struct.pack("!IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        for ts, frame in packets:
            ts_sec = int(ts)
            ts_usec = int((ts - ts_sec) * 1_000_000)
            caplen = len(frame)
            f.write(struct.pack("!IIII", ts_sec, ts_usec, caplen, caplen))
            f.write(frame)


def main() -> None:
    magic = b"PTC0"
    # SET "answer" "42"
    set_req = magic + bytes([0x01]) + struct.pack("!H", 6) + b"answer" + struct.pack("!H", 2) + b"42"
    # SET response (empty value)
    set_resp = magic + bytes([0x03]) + struct.pack("!H", 0)
    # GET "answer"
    get_req = magic + bytes([0x02]) + struct.pack("!H", 6) + b"answer"
    # GET response "42"
    get_resp = magic + bytes([0x03]) + struct.pack("!H", 2) + b"42"

    src_ip = "127.0.0.1"
    dst_ip = "127.0.0.1"
    client_port = 45678
    server_port = 9999
    seq = 1000
    ack = 2000

    packets = []
    base_ts = 1710000000.0

    for i, (payload, is_client_to_server) in enumerate([(set_req, True), (set_resp, False), (get_req, True), (get_resp, False)]):
        if is_client_to_server:
            sport, dport = client_port, server_port
            saddr, daddr = src_ip, dst_ip
        else:
            sport, dport = server_port, client_port
            saddr, daddr = dst_ip, src_ip
        tcp = build_tcp_packet(sport, dport, seq + i * 100, ack + i * 100, payload)
        ip = build_ipv4_packet(saddr, daddr, 6, tcp)
        frame = build_ethernet_frame(ip)
        packets.append((base_ts + i * 0.001, frame))

    out = os.path.join(os.path.dirname(__file__), "capture.pcap")
    write_pcap(out, packets)
    print(f"Written {out} ({len(packets)} packets)")


if __name__ == "__main__":
    main()
