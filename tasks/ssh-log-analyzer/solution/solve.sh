#!/bin/bash
set -euo pipefail
cd /app

# Step 1: Parse auth.log with AWK to extract all statistics
awk '
/Failed password for / {
    # Extract hour from timestamp (field 3, format HH:MM:SS)
    split($3, t, ":")
    hour = t[1]
    hourly_failed[hour]++

    # Extract username and IP (positional: $9=user, $11=IP for standard lines)
    user = $9
    ip = $11

    failed_user[user]++
    failed_ip[ip]++
    total_failed++
}

/Accepted password for / {
    # Extract username (field 9)
    user = $9
    success_user[user]++
    total_success++
}

END {
    # Find peak hour (most failed attempts)
    max_count = 0
    peak_hour = "00"
    for (h in hourly_failed) {
        if (hourly_failed[h] + 0 > max_count + 0) {
            max_count = hourly_failed[h] + 0
            peak_hour = h
        }
    }

    # Output structured data for Python to consume
    print "TOTAL_FAILED", total_failed
    print "TOTAL_SUCCESS", total_success
    print "PEAK_HOUR", peak_hour

    for (u in failed_user)
        print "FAILED_USER", u, failed_user[u]
    for (ip in failed_ip)
        print "FAILED_IP", ip, failed_ip[ip]
    for (u in success_user)
        print "SUCCESS_USER", u, success_user[u]
}
' /app/auth.log > /tmp/awk_output.txt

# Step 2: Convert AWK output to JSON with Python
python3 << 'PYEOF'
import json

data = {
    "total_failed_attempts": 0,
    "total_successful_logins": 0,
    "failed_attempts_by_user": {},
    "failed_attempts_by_ip": {},
    "successful_logins_by_user": {},
    "peak_attack_hour": "00",
    "brute_force_ips": [],
}

with open("/tmp/awk_output.txt") as f:
    for line in f:
        parts = line.strip().split()
        if not parts:
            continue
        tag = parts[0]
        if tag == "TOTAL_FAILED":
            data["total_failed_attempts"] = int(parts[1])
        elif tag == "TOTAL_SUCCESS":
            data["total_successful_logins"] = int(parts[1])
        elif tag == "PEAK_HOUR":
            data["peak_attack_hour"] = parts[1].zfill(2)
        elif tag == "FAILED_USER":
            data["failed_attempts_by_user"][parts[1]] = int(parts[2])
        elif tag == "FAILED_IP":
            data["failed_attempts_by_ip"][parts[1]] = int(parts[2])
        elif tag == "SUCCESS_USER":
            data["successful_logins_by_user"][parts[1]] = int(parts[2])

# Build brute force IPs: >500 failed, sorted by count desc, alpha asc for ties
brute_force = [
    ip for ip, count in data["failed_attempts_by_ip"].items()
    if count > 500
]
brute_force.sort(key=lambda ip: (-data["failed_attempts_by_ip"][ip], ip))
data["brute_force_ips"] = brute_force

with open("/app/analysis.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Analysis complete: {data['total_failed_attempts']} failed, "
      f"{data['total_successful_logins']} successful, "
      f"{len(data['brute_force_ips'])} brute force IPs")
PYEOF
