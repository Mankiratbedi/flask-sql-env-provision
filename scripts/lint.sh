#!/bin/bash
# lint.sh — Run ruff linter on all Python files in a task
set -euo pipefail

TASK_NAME="${1:?Usage: lint.sh <task-name>}"
TASK_DIR="tasks/${TASK_NAME}"

if [ ! -d "$TASK_DIR" ]; then
    echo "ERROR: Task directory not found: $TASK_DIR"
    exit 1
fi

echo "=== Ruff Lint: $TASK_NAME ==="

# Check if ruff is available
if ! command -v ruff &> /dev/null && ! command -v uvx &> /dev/null; then
    echo "Installing ruff..."
    pip3 install --break-system-packages ruff 2>/dev/null || pip install ruff
fi

# Find all Python files
PY_FILES=$(find "$TASK_DIR" -name "*.py" -type f)

if [ -z "$PY_FILES" ]; then
    echo "No Python files found in $TASK_DIR"
    echo "LINT: SKIPPED"
    exit 0
fi

echo "Checking files:"
echo "$PY_FILES" | while read -r f; do echo "  $f"; done
echo ""

# Run ruff
if command -v uvx &> /dev/null; then
    uvx ruff check $PY_FILES
elif command -v ruff &> /dev/null; then
    ruff check $PY_FILES
fi

RESULT=$?

echo ""
if [ "$RESULT" -eq 0 ]; then
    echo "LINT: PASSED"
else
    echo "LINT: FAILED"
    echo "Run 'ruff check --fix' to auto-fix issues"
fi

exit $RESULT
