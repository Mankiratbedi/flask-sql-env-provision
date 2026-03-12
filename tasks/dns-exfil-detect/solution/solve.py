#!/usr/bin/env python3
"""Oracle solution for dns-exfil-detect.

Analyzes the PCAP to find DNS exfiltration queries, decodes the custom encoding,
reconstructs the stolen data, and writes results to /app/results.json.
"""
import hashlib
import json
import struct


def parse_dns_qname(data: bytes, offset: int) -> tuple[str, int]:
    """Parse a DNS QNAME from raw packet data starting at offset."""
    labels = []
    while True:
        if offset >= len(data):
            break
        length = data[offset]
        if length == 0:
            offset += 1
            break
        if (length & 0xC0) == 0xC0:
            # Compressed label — skip
            offset += 2
            break
        offset += 1
        label = data[offset:offset + length].decode("ascii", errors="replace")
        labels.append(label)
        offset += length
    return ".".join(labels), offset


def extract_dns_queries_from_pcap(pcap_path: str) -> list[str]:
    """Extract all DNS query names from a PCAP file."""
    queries = []

    with open(pcap_path, "rb") as f:
        # Read global header (24 bytes)
        global_header = f.read(24)
        if len(global_header) < 24:
            return queries

        magic = struct.unpack("!I", global_header[0:4])[0]
        if magic == 0xa1b2c3d4:
            endian = "!"  # big endian
        elif magic == 0xd4c3b2a1:
            endian = "<"  # little endian
        else:
            return queries

        # Read packets
        while True:
            # Packet header (16 bytes)
            pkt_header = f.read(16)
            if len(pkt_header) < 16:
                break

            ts_sec, ts_usec, caplen, origlen = struct.unpack(f"{endian}IIII", pkt_header)

            pkt_data = f.read(caplen)
            if len(pkt_data) < caplen:
                break

            # Parse: Ethernet (14) + IPv4 (20) + UDP (8) + DNS
            if caplen < 14 + 20 + 8 + 12:
                continue

            # Check EtherType = IPv4 (0x0800)
            ethertype = struct.unpack("!H", pkt_data[12:14])[0]
            if ethertype != 0x0800:
                continue

            # Check IP protocol = UDP (17)
            ip_protocol = pkt_data[14 + 9]
            if ip_protocol != 17:
                continue

            # Check destination port = 53
            udp_offset = 14 + 20
            dst_port = struct.unpack("!H", pkt_data[udp_offset + 2:udp_offset + 4])[0]
            if dst_port != 53:
                continue

            # Parse DNS query name
            dns_offset = udp_offset + 8  # UDP header is 8 bytes
            # Skip DNS header (12 bytes) to get to question section
            question_offset = dns_offset + 12

            if question_offset < len(pkt_data):
                qname, _ = parse_dns_qname(pkt_data, question_offset)
                if qname:
                    queries.append(qname)

    return queries


def custom_decode(encoded: str) -> bytes:
    """Reverse the custom encoding: custom base16 decode, then XOR with 0x5A."""
    alphabet = "QWERTYUIOPASDFGH"
    char_to_val = {c: i for i, c in enumerate(alphabet)}

    decoded_bytes = []
    for i in range(0, len(encoded), 2):
        if i + 1 >= len(encoded):
            break
        high = char_to_val.get(encoded[i], 0)
        low = char_to_val.get(encoded[i + 1], 0)
        byte = (high << 4) | low
        decoded_bytes.append(byte ^ 0x5A)

    return bytes(decoded_bytes)


def main():
    pcap_path = "/app/traffic.pcap"
    c2_domain = "data.c2server.internal"

    # Extract all DNS queries
    all_queries = extract_dns_queries_from_pcap(pcap_path)

    # Filter exfiltration queries
    c2_suffix = f".{c2_domain}"
    exfil_queries = [q for q in all_queries if q.endswith(c2_suffix)]

    # Parse sequence numbers and encoded chunks
    chunks = {}
    for query in exfil_queries:
        # Strip the c2 domain suffix
        prefix = query[: -(len(c2_suffix))]
        parts = prefix.split(".", 1)
        if len(parts) == 2:
            seq = int(parts[0])
            encoded_chunk = parts[1]
            chunks[seq] = encoded_chunk

    # Decode chunks in order
    decoded_parts = []
    for seq in sorted(chunks.keys()):
        decoded = custom_decode(chunks[seq])
        decoded_parts.append(decoded)

    decoded_content = b"".join(decoded_parts).decode("utf-8")
    sha256 = hashlib.sha256(decoded_content.encode("utf-8")).hexdigest()

    results = {
        "c2_domain": c2_domain,
        "num_exfil_queries": len(exfil_queries),
        "decoded_content": decoded_content,
        "sha256": sha256,
    }

    with open("/app/results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Results written to /app/results.json")
    print(f"C2 domain: {c2_domain}")
    print(f"Exfil queries found: {len(exfil_queries)}")
    print(f"SHA-256: {sha256}")


if __name__ == "__main__":
    main()
