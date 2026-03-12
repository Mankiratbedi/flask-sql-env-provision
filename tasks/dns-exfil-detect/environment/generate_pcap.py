#!/usr/bin/env python3
"""Generate a PCAP file with legitimate DNS traffic and hidden DNS exfiltration.

The exfiltration uses a custom encoding:
  1. XOR each byte with 0x5A
  2. Encode with a non-standard base32 alphabet: QWERTYUIOPASDFGH

Exfil queries target: data.c2server.internal
Format: <seq_number>.<encoded_chunk>.data.c2server.internal

This script is deterministic (seeded RNG) so the PCAP is reproducible.
"""
import random
import hashlib
import struct
import socket
import os

SEED = 20260312
random.seed(SEED)

# --- Custom encoding ---
CUSTOM_B32_ALPHABET = "QWERTYUIOPASDFGH"
XOR_KEY = 0x5A


def custom_encode(data: bytes) -> str:
    """XOR each byte with 0x5A, then encode with custom base32 alphabet."""
    xored = bytes(b ^ XOR_KEY for b in data)
    # Simple base16 (hex-like) using our custom 16-char alphabet
    result = []
    for byte in xored:
        high = (byte >> 4) & 0x0F
        low = byte & 0x0F
        result.append(CUSTOM_B32_ALPHABET[high])
        result.append(CUSTOM_B32_ALPHABET[low])
    return "".join(result)


# --- DNS packet construction (raw bytes, no scapy dependency) ---

def build_dns_query(qname: str, query_id: int = None) -> bytes:
    """Build a minimal DNS query packet (UDP payload)."""
    if query_id is None:
        query_id = random.randint(0, 65535)

    # Header: ID, flags=0x0100 (standard query), QDCOUNT=1
    header = struct.pack("!HHHHHH", query_id, 0x0100, 1, 0, 0, 0)

    # Question section: encode QNAME
    question = b""
    for label in qname.split("."):
        question += struct.pack("!B", len(label)) + label.encode("ascii")
    question += b"\x00"  # root label
    question += struct.pack("!HH", 1, 1)  # QTYPE=A, QCLASS=IN

    return header + question


def build_udp_packet(src_port: int, dst_port: int, payload: bytes) -> bytes:
    """Build a UDP header + payload."""
    length = 8 + len(payload)
    # Checksum = 0 (optional in IPv4 UDP)
    header = struct.pack("!HHHH", src_port, dst_port, length, 0)
    return header + payload


def build_ipv4_packet(src_ip: str, dst_ip: str, protocol: int, payload: bytes) -> bytes:
    """Build a minimal IPv4 header + payload."""
    version_ihl = 0x45
    dscp_ecn = 0
    total_length = 20 + len(payload)
    identification = random.randint(0, 65535)
    flags_offset = 0x4000  # Don't fragment
    ttl = 64
    checksum = 0  # Will calculate

    src = socket.inet_aton(src_ip)
    dst = socket.inet_aton(dst_ip)

    header = struct.pack("!BBHHHBBH4s4s",
                         version_ihl, dscp_ecn, total_length,
                         identification, flags_offset,
                         ttl, protocol, checksum,
                         src, dst)

    # Calculate checksum
    words = struct.unpack("!10H", header)
    s = sum(words)
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    checksum = ~s & 0xFFFF

    header = struct.pack("!BBHHHBBH4s4s",
                         version_ihl, dscp_ecn, total_length,
                         identification, flags_offset,
                         ttl, protocol, checksum,
                         src, dst)

    return header + payload


def build_ethernet_frame(payload: bytes) -> bytes:
    """Build an Ethernet II frame."""
    dst_mac = b"\x00\x1a\x2b\x3c\x4d\x5e"
    src_mac = b"\x00\x5e\x4d\x3c\x2b\x1a"
    ethertype = struct.pack("!H", 0x0800)  # IPv4
    return dst_mac + src_mac + ethertype + payload


def write_pcap(filename: str, packets: list[tuple[float, bytes]]):
    """Write packets to a PCAP file.

    packets: list of (timestamp_seconds, raw_ethernet_frame)
    """
    with open(filename, "wb") as f:
        # Global header
        f.write(struct.pack("!IHHiIII",
                            0xa1b2c3d4,  # magic
                            2, 4,        # version
                            0,           # thiszone
                            0,           # sigfigs
                            65535,       # snaplen
                            1))          # network (Ethernet)

        for ts, frame in packets:
            ts_sec = int(ts)
            ts_usec = int((ts - ts_sec) * 1_000_000)
            caplen = len(frame)
            f.write(struct.pack("!IIII", ts_sec, ts_usec, caplen, caplen))
            f.write(frame)


def make_dns_packet(src_ip: str, dst_ip: str, qname: str, src_port: int = None) -> bytes:
    """Build a complete Ethernet frame containing a DNS query."""
    if src_port is None:
        src_port = random.randint(1024, 65535)
    dns = build_dns_query(qname)
    udp = build_udp_packet(src_port, 53, dns)
    ip = build_ipv4_packet(src_ip, dst_ip, 17, udp)  # 17 = UDP
    return build_ethernet_frame(ip)


def main():
    # --- Secret data to exfiltrate ---
    secret_message = (
        "CONFIDENTIAL: Project Aurora credentials\n"
        "DB_HOST=prod-aurora-db.internal.corp\n"
        "DB_USER=admin_service\n"
        "DB_PASS=Kx9$mP2!vL7@nQ4\n"
        "API_KEY=sk-proj-8f3a2c1d9e7b4a6f0h5i\n"
        "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE\n"
        "AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n"
        "INTERNAL_ENDPOINT=https://api.internal.corp/v2/admin\n"
        "ENCRYPTION_MASTER_KEY=aes256-gcm-0x4f8a2c1d3e7b9f0a\n"
    )

    sha256 = hashlib.sha256(secret_message.encode("utf-8")).hexdigest()
    print(f"Secret message SHA-256: {sha256}")
    print(f"Secret message length: {len(secret_message)} bytes")

    # --- Chunk the secret into DNS-label-safe sizes ---
    chunk_size = 20  # bytes per chunk before encoding
    secret_bytes = secret_message.encode("utf-8")
    chunks = []
    for i in range(0, len(secret_bytes), chunk_size):
        chunks.append(secret_bytes[i:i + chunk_size])

    print(f"Number of exfil chunks: {len(chunks)}")

    c2_domain = "data.c2server.internal"

    # --- Generate exfil queries ---
    exfil_queries = []
    for seq, chunk in enumerate(chunks):
        encoded = custom_encode(chunk)
        qname = f"{seq}.{encoded}.{c2_domain}"
        exfil_queries.append(qname)

    # --- Legitimate domains ---
    legit_domains = [
        "google.com", "www.google.com", "mail.google.com",
        "cloudflare.com", "one.one.one.one",
        "github.com", "api.github.com",
        "amazonaws.com", "s3.amazonaws.com",
        "microsoft.com", "login.microsoftonline.com",
        "apple.com", "icloud.com",
        "facebook.com", "cdn.facebook.com",
        "twitter.com", "api.twitter.com",
        "linkedin.com", "www.linkedin.com",
        "stackoverflow.com",
        "npmjs.com", "registry.npmjs.com",
        "pypi.org", "files.pythonhosted.org",
        "ubuntu.com", "archive.ubuntu.com",
        "docker.io", "registry.docker.io",
        "slack.com", "api.slack.com",
        "zoom.us", "us02web.zoom.us",
        "dropbox.com", "dl.dropboxusercontent.com",
        "atlassian.com", "jira.atlassian.com",
        "notion.so", "api.notion.so",
        "vercel.app", "vercel.com",
        "netlify.com", "app.netlify.com",
        "datadog.com", "api.datadoghq.com",
        "sentry.io", "o1.ingest.sentry.io",
        "grafana.com", "prometheus.io",
        "elastic.co", "kibana.elastic.co",
        "redis.io", "mongodb.com",
    ]

    # Also add some subdomains with random prefixes to make traffic look realistic
    random_prefixes = ["cdn", "api", "static", "assets", "img", "media", "edge", "lb", "cache"]

    # --- Build all packets ---
    packets = []
    base_time = 1710000000.0  # ~March 2024

    # Internal network IPs
    client_ips = [f"10.0.1.{i}" for i in range(10, 60)]
    dns_server = "10.0.0.53"

    # Attacker's machine (blends in with other clients)
    attacker_ip = "10.0.1.37"

    num_legit_queries = 50000

    # Generate legitimate traffic timestamps
    legit_times = sorted([base_time + random.uniform(0, 7200) for _ in range(num_legit_queries)])

    # Generate exfil timestamps — spread across the 2-hour window, slightly clustered
    exfil_start = base_time + random.uniform(300, 600)  # start 5-10 min in
    exfil_times = sorted([
        exfil_start + (i * (6000 / len(exfil_queries))) + random.uniform(-5, 5)
        for i in range(len(exfil_queries))
    ])

    # Merge all events by time
    events = []
    for t in legit_times:
        domain = random.choice(legit_domains)
        # Sometimes add a random subdomain prefix
        if random.random() < 0.15:
            prefix = random.choice(random_prefixes)
            domain = f"{prefix}.{domain}"
        client = random.choice(client_ips)
        events.append((t, client, domain, "legit"))

    for i, t in enumerate(exfil_times):
        events.append((t, attacker_ip, exfil_queries[i], "exfil"))

    # Sort by timestamp
    events.sort(key=lambda x: x[0])

    for ts, src_ip, qname, _ in events:
        frame = make_dns_packet(src_ip, dns_server, qname)
        packets.append((ts, frame))

    print(f"Total packets: {len(packets)}")
    print(f"Legit: {num_legit_queries}, Exfil: {len(exfil_queries)}")

    # --- Write PCAP ---
    output_path = os.path.join(os.path.dirname(__file__), "traffic.pcap")
    write_pcap(output_path, packets)
    print(f"PCAP written to: {output_path}")
    print(f"C2 domain: {c2_domain}")
    print(f"Num exfil queries: {len(exfil_queries)}")


if __name__ == "__main__":
    main()
