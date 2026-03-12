#!/bin/bash
# run_oracle.sh — Run oracle validation via Harbor (solution runs, tests must pass)
set -uo pipefail

TASK_NAME="${1:?Usage: run_oracle.sh <task-name>}"
TASK_DIR="tasks/${TASK_NAME}"

if [ ! -d "$TASK_DIR" ]; then
    echo "ERROR: Task directory not found: $TASK_DIR"
    exit 1
fi

echo "=== Oracle Validation: $TASK_NAME ==="
uv run harbor run --agent oracle --path "$TASK_DIR"
exit $?
