# SSH Log Analyzer

## Context

You are a security analyst responding to a potential brute-force attack on a server. The file `/app/auth.log` contains SSH authentication log data with approximately 50,300 log lines covering January. Your task is to analyze this log file using **AWK as the primary analysis tool** (with bash and python3 available as helpers) to extract key security metrics and output a structured JSON report.

## Log Format

Each line in `/app/auth.log` follows the standard syslog format for SSH authentication events. Examples:

```
Jan  1 02:00:00 server01 sshd[10001]: Failed password for root from 203.0.113.1 port 12345 ssh2
Jan 10 09:15:32 server01 sshd[20001]: Accepted password for alice from 10.0.0.10 port 22001 ssh2
```

- **Failed attempts** contain the string `Failed password for`
- **Successful logins** contain the string `Accepted password for`
- The timestamp is in fields 1-3 (month, day, HH:MM:SS)
- The username appears after `for` (field 9 in standard format)
- The source IP address appears after `from` (field 11 in standard format)
- The hour of the event is the first two characters of field 3 (HH:MM:SS)

## Task

Write a solution using AWK as the primary analysis tool to extract the following statistics from `/app/auth.log`:

1. **Total number of failed login attempts** — count of all lines containing `Failed password for`
2. **Total number of successful logins** — count of all lines containing `Accepted password for`
3. **Failed login counts per username** — for every username that appears in a failed login line, count how many times it appears
4. **Failed login counts per source IP address** — for every source IP that appears in a failed login line, count how many times it appears
5. **Successful login counts per username** — for every username that appears in a successful login line, count how many times it appears
6. **Peak attack hour** — the hour of day (00–23, zero-padded to 2 digits) with the most failed login attempts
7. **Brute force IPs** — the list of all IP addresses with **strictly more than 500** failed login attempts, sorted by failed attempt count in **descending order**; for ties in count, sort alphabetically ascending by IP address as a tiebreaker

## Output

Write the analysis results to `/app/analysis.json` with this **exact** JSON schema:

```json
{
  "total_failed_attempts": <integer>,
  "total_successful_logins": <integer>,
  "failed_attempts_by_user": {"<username>": <integer>, ...},
  "failed_attempts_by_ip": {"<ip>": <integer>, ...},
  "successful_logins_by_user": {"<username>": <integer>, ...},
  "peak_attack_hour": "<HH>",
  "brute_force_ips": ["<ip>", ...]
}
```

### Field Requirements

- **`total_failed_attempts`**: Integer. Total count of failed SSH login attempts.
- **`total_successful_logins`**: Integer. Total count of successful SSH logins.
- **`failed_attempts_by_user`**: Object mapping each username to its integer failed attempt count. Include ALL usernames that appear in failed login lines.
- **`failed_attempts_by_ip`**: Object mapping each source IP address to its integer failed attempt count. Include ALL IPs that appear in failed login lines.
- **`successful_logins_by_user`**: Object mapping each username to its integer successful login count. Include ALL usernames that appear in successful login lines.
- **`peak_attack_hour`**: String. The 2-digit zero-padded hour (e.g., `"02"` not `"2"`) with the highest number of failed login attempts. Must be a string of exactly 2 characters.
- **`brute_force_ips`**: Array of IP address strings. Contains only IPs with **strictly more than 500** failed attempts (i.e., IPs with exactly 500 attempts are **NOT** included). Sorted by failed attempt count descending; alphabetical ascending for ties.

## Requirements Summary

- Use AWK as the primary parsing tool for `/app/auth.log`
- Output file must be at `/app/analysis.json`
- All counts must be exact integers (no approximations)
- `peak_attack_hour` must be a zero-padded 2-character string
- `brute_force_ips` must be sorted by count descending, with alphabetical ascending as tiebreaker for equal counts
- The threshold for `brute_force_ips` is **strictly greater than 500** (not greater than or equal to)
