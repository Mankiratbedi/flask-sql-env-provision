# DNS Exfiltration Detection & Decoding

## Background

You are a security analyst investigating a suspected data breach. A network capture file has been collected from a corporate DNS server containing approximately 2 hours of DNS traffic. Intelligence suggests that an attacker exfiltrated sensitive data by encoding it into DNS query subdomain labels — a technique known as DNS tunneling/exfiltration.

Your job is to find the exfiltration traffic, decode the stolen data, and produce a forensic report.

## Environment

- A PCAP file is located at `/app/traffic.pcap`
- The following tools are available: `python3`, `tshark`, `tcpdump`
- The `scapy` Python library is pre-installed for programmatic PCAP analysis

## Task

### Step 1: Identify Exfiltration Traffic

Analyze `/app/traffic.pcap` to distinguish malicious DNS exfiltration queries from legitimate DNS traffic. The PCAP contains a mix of:
- **Legitimate DNS queries** to common domains (e.g., `google.com`, `cloudflare.com`, `github.com`, etc.)
- **Exfiltration queries** that encode stolen data in the subdomain labels of queries to a command-and-control domain

The exfiltration queries target a specific C2 domain. You must identify this domain by analyzing query patterns and subdomain characteristics.

### Step 2: Decode the Exfiltrated Data

The exfiltration uses a **custom encoding scheme** — standard base32/base64 decoders will NOT work. You must:
1. Extract the encoded subdomain labels from the exfiltration queries
2. Reverse-engineer the encoding by analyzing the character set and patterns
3. Decode the data to recover the original stolen content

**Hints:**
- The encoding uses a non-standard alphabet
- There may be a byte-level transformation applied before the alphabet encoding
- Each exfiltration query carries a chunk of the data; chunks are sequenced by a numeric prefix in the subdomain label (e.g., `<seq>.<encoded_chunk>.domain`)

### Step 3: Reconstruct and Report

After decoding all chunks (ordered by sequence number), concatenate them to reconstruct the stolen file.

Write your results to `/app/results.json` with the following exact JSON schema:

```json
{
  "c2_domain": "<the command-and-control domain used for exfiltration>",
  "num_exfil_queries": <integer — number of exfiltration DNS queries found>,
  "decoded_content": "<the full decoded/reconstructed stolen data as a string>",
  "sha256": "<SHA-256 hex digest of the decoded content string (UTF-8 encoded)>"
}
```

**Field specifications:**
- `c2_domain`: The full domain suffix used for exfiltration (e.g., `evil.example.com`), excluding any subdomain labels that carry data
- `num_exfil_queries`: Total count of DNS queries identified as exfiltration
- `decoded_content`: The complete reconstructed stolen data as a UTF-8 string
- `sha256`: The SHA-256 hash of the `decoded_content` string, computed as `hashlib.sha256(decoded_content.encode("utf-8")).hexdigest()`

## Constraints

- All analysis must be performed locally using the provided tools
- Do NOT rely on external services or internet access
- Output MUST be written to `/app/results.json`
