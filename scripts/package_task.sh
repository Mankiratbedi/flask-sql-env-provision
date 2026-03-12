#!/bin/bash
# package_task.sh — Create a .zip file of the task for submission
set -euo pipefail

TASK_NAME="${1:?Usage: package_task.sh <task-name>}"
TASK_DIR="tasks/${TASK_NAME}"
OUTPUT_DIR="ready_to_submit"
ZIP_FILE="${OUTPUT_DIR}/${TASK_NAME}.zip"

if [ ! -d "$TASK_DIR" ]; then
    echo "ERROR: Task directory not found: $TASK_DIR"
    exit 1
fi

echo "=== Packaging: $TASK_NAME ==="

# Verify required files exist
MISSING=0
for required in "task.toml" "instruction.md" "environment/Dockerfile" "solution/solve.sh" "tests/test.sh"; do
    if [ ! -f "$TASK_DIR/$required" ]; then
        echo "  MISSING: $TASK_DIR/$required"
        MISSING=$((MISSING + 1))
    fi
done

if [ "$MISSING" -gt 0 ]; then
    echo "ERROR: $MISSING required file(s) missing. Cannot package."
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Remove old zip if exists
rm -f "$ZIP_FILE"

# Create zip from tasks directory
cd tasks
zip -r "../$ZIP_FILE" "$TASK_NAME/" -x '*/__pycache__/*' '*/.DS_Store'
cd ..

echo ""
echo "PACKAGING: DONE"
echo "Created: $ZIP_FILE"
echo "Size: $(du -h "$ZIP_FILE" | cut -f1)"
echo ""
echo "Ready for submission to TB 3.0 repo!"
