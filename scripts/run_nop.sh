#!/bin/bash
# run_nop.sh — Run no-op validation via Harbor (no solution, tests must fail)
set -uo pipefail

TASK_NAME="${1:?Usage: run_nop.sh <task-name>}"
TASK_DIR="tasks/${TASK_NAME}"

if [ ! -d "$TASK_DIR" ]; then
    echo "ERROR: Task directory not found: $TASK_DIR"
    exit 1
fi

echo "=== No-Op Validation: $TASK_NAME ==="
uv run harbor run --agent nop --path "$TASK_DIR"
exit $?
