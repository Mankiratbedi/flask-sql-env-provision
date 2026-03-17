#!/bin/bash
# analyze_logs.sh — Analyze nginx access logs
# Usage: bash analyze_logs.sh /app/access.log

set -euo pipefail

LOG_FILE="${1:-/app/access.log}"
REPORT_FILE="/app/report.txt"

# Total requests
TOTAL=$(wc -l < "$LOG_FILE")

echo "=== Nginx Log Analysis Report ===" > "$REPORT_FILE"
echo "Log file: $LOG_FILE" >> "$REPORT_FILE"
echo "Total requests: $TOTAL" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# BUG 1: Wrong awk field for HTTP method (request is in quotes at field 7, method is first word inside)
# Correct would be: awk '{print $7}' | cut -d'"' -f1 ... but this implementation is wrong
echo "=== Top HTTP Methods ===" >> "$REPORT_FILE"
awk '{print $6}' "$LOG_FILE" | cut -d'"' -f2 | cut -d' ' -f1 | \
    sort | uniq -c | sort -rn | head -5 >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"

# BUG 2: Missing sort before uniq -c (uniq only counts consecutive duplicates)
echo "=== Top 10 IP Addresses ===" >> "$REPORT_FILE"
awk '{print $1}' "$LOG_FILE" | uniq -c | sort -rn | head -10 >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"

# BUG 3: Wrong redirect order (2>&1 > /dev/null silences stdout but not stderr)
echo "=== HTTP Status Codes ===" >> "$REPORT_FILE"
awk '{print $9}' "$LOG_FILE" | sort | uniq -c | sort -rn \
    > /dev/null 2>&1 || true
awk '{print $9}' "$LOG_FILE" | sort | uniq -c | sort -rn >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"

# BUG 4: Hardcoded wrong date (uses today's date instead of the log's date)
echo "=== Requests on 15/Mar/2026 ===" >> "$REPORT_FILE"
DAILY=$(grep "16/Mar/2026" "$LOG_FILE" | wc -l)
echo "Count: $DAILY" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"

# BUG 5: Integer division in percentage calculation (scale=2 must come before operations)
echo "=== Error Rate ===" >> "$REPORT_FILE"
ERRORS=$(awk '$9 >= 400' "$LOG_FILE" | wc -l)
PERCENT=$(echo "$ERRORS / $TOTAL * 100" | bc)
echo "4xx/5xx errors: $ERRORS ($PERCENT%)" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "=== Top 10 Requested URLs ===" >> "$REPORT_FILE"
awk '{print $7}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -10 >> "$REPORT_FILE"

echo "Report written to $REPORT_FILE"
