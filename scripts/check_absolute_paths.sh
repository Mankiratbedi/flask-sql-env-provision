#!/bin/bash
# check_absolute_paths.sh — Scan for hardcoded host-machine absolute paths
set -euo pipefail

TASK_NAME="${1:?Usage: check_absolute_paths.sh <task-name>}"
TASK_DIR="tasks/${TASK_NAME}"

if [ ! -d "$TASK_DIR" ]; then
    echo "ERROR: Task directory not found: $TASK_DIR"
    exit 1
fi

echo "=== Absolute Path Check: $TASK_NAME ==="

# Patterns that indicate host-machine paths (not container paths)
# Container paths like /app, /tests, /solution, /logs are fine
ISSUES=0

# Check for common host-machine path patterns
while IFS= read -r file; do
    # Skip binary files and .git
    if file "$file" | grep -q "text"; then
        # Check for host paths (home dirs, Users, etc.)
        if grep -nE '(/home/[a-zA-Z]|/Users/[a-zA-Z]|/mnt/|/tmp/[a-zA-Z]|C:\\\\|D:\\\\)' "$file" 2>/dev/null; then
            echo "  WARNING: Host-machine path found in $file"
            ISSUES=$((ISSUES + 1))
        fi
    fi
done < <(find "$TASK_DIR" -type f -not -path '*/.git/*')

# Check that tests/solution are NOT referenced in Dockerfile COPY
DOCKERFILE="$TASK_DIR/environment/Dockerfile"
if [ -f "$DOCKERFILE" ]; then
    if grep -nEi '(COPY.*tests|COPY.*solution|ADD.*tests|ADD.*solution)' "$DOCKERFILE" 2>/dev/null; then
        echo "  ERROR: Dockerfile copies tests/ or solution/ into the image!"
        ISSUES=$((ISSUES + 1))
    fi
fi

echo ""
if [ "$ISSUES" -eq 0 ]; then
    echo "ABSOLUTE PATH CHECK: PASSED"
    echo "No host-machine paths or forbidden copies found."
    exit 0
else
    echo "ABSOLUTE PATH CHECK: FAILED"
    echo "Found $ISSUES issue(s). Fix the paths above."
    exit 1
fi
