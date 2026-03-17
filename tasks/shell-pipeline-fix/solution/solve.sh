#!/bin/bash
set -euo pipefail

cat > /app/analyze_logs.sh << 'SCRIPT'
#!/bin/bash
# analyze_logs.sh — Analyze nginx access logs (fixed version)
set -euo pipefail

LOG_FILE="${1:-/app/access.log}"
REPORT_FILE="/app/report.txt"

TOTAL=$(wc -l < "$LOG_FILE")

echo "=== Nginx Log Analysis Report ===" > "$REPORT_FILE"
echo "Log file: $LOG_FILE" >> "$REPORT_FILE"
echo "Total requests: $TOTAL" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# FIX 1: Correctly extract HTTP method from quoted request field
echo "=== Top HTTP Methods ===" >> "$REPORT_FILE"
awk '{print $6}' "$LOG_FILE" | cut -d'"' -f2 | cut -d' ' -f1 | \
    sort | uniq -c | sort -rn | head -5 >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"

# FIX 2: Add sort before uniq -c so all duplicates are counted
echo "=== Top 10 IP Addresses ===" >> "$REPORT_FILE"
awk '{print $1}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -10 >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"

# FIX 3: Correct redirect order (> /dev/null 2>&1)
echo "=== HTTP Status Codes ===" >> "$REPORT_FILE"
awk '{print $9}' "$LOG_FILE" | sort | uniq -c | sort -rn >> "$REPORT_FILE" 2>/dev/null || \
awk '{print $9}' "$LOG_FILE" | sort | uniq -c | sort -rn >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"

# FIX 4: Use the correct date (15/Mar/2026, the main log day)
echo "=== Requests on 15/Mar/2026 ===" >> "$REPORT_FILE"
DAILY=$(grep "15/Mar/2026" "$LOG_FILE" | wc -l)
echo "Count: $DAILY" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"

# FIX 5: Use scale=2 for decimal percentage calculation
echo "=== Error Rate ===" >> "$REPORT_FILE"
ERRORS=$(awk '$9 >= 400' "$LOG_FILE" | wc -l)
PERCENT=$(echo "scale=2; $ERRORS * 100 / $TOTAL" | bc)
echo "4xx/5xx errors: $ERRORS ($PERCENT%)" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "=== Top 10 Requested URLs ===" >> "$REPORT_FILE"
awk '{print $7}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -10 >> "$REPORT_FILE"

echo "Report written to $REPORT_FILE"
SCRIPT

chmod +x /app/analyze_logs.sh
bash /app/analyze_logs.sh /app/access.log
echo "--- Report ---"
cat /app/report.txt
