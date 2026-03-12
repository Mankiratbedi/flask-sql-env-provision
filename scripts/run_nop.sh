#!/bin/bash
# run_nop.sh — Build Docker image, run tests WITHOUT solution, verify they FAIL
set -uo pipefail

TASK_NAME="${1:?Usage: run_nop.sh <task-name>}"
TASK_DIR="tasks/${TASK_NAME}"
IMAGE_NAME="tb3-${TASK_NAME}"
CONTAINER_NAME="tb3-nop-${TASK_NAME}"

if [ ! -d "$TASK_DIR" ]; then
    echo "ERROR: Task directory not found: $TASK_DIR"
    exit 1
fi

# Cleanup leftover container
docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1 || true

echo "=== No-Op Validation: $TASK_NAME ==="

# Step 1: Build Docker image (reuse cache)
echo "[1/4] Building Docker image..."
docker build -t "$IMAGE_NAME" "$TASK_DIR/environment/"
if [ $? -ne 0 ]; then
    echo "NO-OP VALIDATION: FAILED (Docker build failed)"
    exit 1
fi

# Step 2: Start container
echo "[2/4] Starting container..."
docker run -d --name "$CONTAINER_NAME" "$IMAGE_NAME" tail -f /dev/null > /dev/null

# Step 3: Copy ONLY tests (NO solution), run them
echo "[3/4] Running tests without solution (no-op)..."
docker exec "$CONTAINER_NAME" mkdir -p /tests /logs/verifier
docker cp "$TASK_DIR/tests/." "$CONTAINER_NAME:/tests/"

docker exec "$CONTAINER_NAME" bash -c "cd /app && bash /tests/test.sh" 2>&1 || true

# Step 4: Check results — tests SHOULD fail
echo "[4/4] Checking results..."

CTRF_EXISTS=$(docker exec "$CONTAINER_NAME" test -f /logs/verifier/ctrf.json && echo "yes" || echo "no")
REWARD_EXISTS=$(docker exec "$CONTAINER_NAME" test -f /logs/verifier/reward.txt && echo "yes" || echo "no")

TESTS_FAILED="unknown"
if [ "$CTRF_EXISTS" = "yes" ]; then
    FAILED_COUNT=$(docker exec "$CONTAINER_NAME" python3 -c "
import json
with open('/logs/verifier/ctrf.json') as f:
    data = json.load(f)
summary = data.get('results', {}).get('summary', {})
print(summary.get('failed', 0) + summary.get('other', 0))
" 2>/dev/null || echo "-1")
    if [ "$FAILED_COUNT" != "0" ] && [ "$FAILED_COUNT" != "-1" ]; then
        TESTS_FAILED="yes"
    elif [ "$FAILED_COUNT" = "0" ]; then
        TESTS_FAILED="no"
    fi
elif [ "$REWARD_EXISTS" = "yes" ]; then
    REWARD=$(docker exec "$CONTAINER_NAME" cat /logs/verifier/reward.txt 2>/dev/null)
    if [ "$REWARD" = "0" ]; then
        TESTS_FAILED="yes"
    else
        TESTS_FAILED="no"
    fi
else
    # No result files — test.sh probably crashed, which means tests didn't pass
    TESTS_FAILED="yes"
fi

# Cleanup
docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1

echo ""
if [ "$TESTS_FAILED" = "yes" ]; then
    echo "NO-OP VALIDATION: PASSED ✓"
    echo "  - Tests correctly FAIL without solution"
    exit 0
elif [ "$TESTS_FAILED" = "no" ]; then
    echo "NO-OP VALIDATION: FAILED ✗"
    echo "  - Tests PASSED without solution — task may be trivial!"
    echo "  - Check that tests actually verify the solution's output"
    exit 1
else
    echo "NO-OP VALIDATION: WARNING"
    echo "  - Could not determine test results"
    echo "  - Check test.sh output manually"
    exit 1
fi
