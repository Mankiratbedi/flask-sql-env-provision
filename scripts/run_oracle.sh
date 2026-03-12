#!/bin/bash
# run_oracle.sh — Build Docker image, run oracle solution, verify tests pass
# Harbor uses ctrf.json for reward. Our script checks both ctrf.json and reward.txt.
set -uo pipefail

TASK_NAME="${1:?Usage: run_oracle.sh <task-name>}"
TASK_DIR="tasks/${TASK_NAME}"
IMAGE_NAME="tb3-${TASK_NAME}"
CONTAINER_NAME="tb3-oracle-${TASK_NAME}"

if [ ! -d "$TASK_DIR" ]; then
    echo "ERROR: Task directory not found: $TASK_DIR"
    exit 1
fi

# Cleanup leftover container
docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1 || true

echo "=== Oracle Validation: $TASK_NAME ==="

# Step 1: Build Docker image
echo "[1/5] Building Docker image..."
docker build -t "$IMAGE_NAME" "$TASK_DIR/environment/"
if [ $? -ne 0 ]; then
    echo "ORACLE VALIDATION: FAILED (Docker build failed)"
    exit 1
fi

# Step 2: Start container (keep alive for exec)
echo "[2/5] Starting container..."
docker run -d --name "$CONTAINER_NAME" "$IMAGE_NAME" tail -f /dev/null > /dev/null
if [ $? -ne 0 ]; then
    echo "ORACLE VALIDATION: FAILED (Container failed to start)"
    exit 1
fi

# Step 3: Copy solution and tests, run oracle
echo "[3/5] Running oracle solution..."
docker exec "$CONTAINER_NAME" mkdir -p /solution /tests /logs/verifier
docker cp "$TASK_DIR/solution/." "$CONTAINER_NAME:/solution/"
docker cp "$TASK_DIR/tests/." "$CONTAINER_NAME:/tests/"
docker exec "$CONTAINER_NAME" chmod +x /solution/solve.sh

docker exec "$CONTAINER_NAME" bash -c "cd /app && bash /solution/solve.sh"
SOLVE_EXIT=$?
if [ $SOLVE_EXIT -ne 0 ]; then
    echo "WARNING: solve.sh exited with code $SOLVE_EXIT"
fi

# Step 4: Run tests
echo "[4/5] Running tests..."
docker exec "$CONTAINER_NAME" bash -c "cd /app && bash /tests/test.sh"
TEST_EXIT=$?

# Step 5: Check results
echo "[5/5] Checking results..."

# Check ctrf.json first (new Harbor format), then reward.txt (legacy)
CTRF_EXISTS=$(docker exec "$CONTAINER_NAME" test -f /logs/verifier/ctrf.json && echo "yes" || echo "no")
REWARD_EXISTS=$(docker exec "$CONTAINER_NAME" test -f /logs/verifier/reward.txt && echo "yes" || echo "no")

PASSED="unknown"
if [ "$CTRF_EXISTS" = "yes" ]; then
    # Parse ctrf.json — all tests must pass
    FAILED_COUNT=$(docker exec "$CONTAINER_NAME" python3 -c "
import json
with open('/logs/verifier/ctrf.json') as f:
    data = json.load(f)
summary = data.get('results', {}).get('summary', {})
print(summary.get('failed', -1) + summary.get('other', 0))
" 2>/dev/null || echo "-1")
    if [ "$FAILED_COUNT" = "0" ]; then
        PASSED="yes"
    else
        PASSED="no"
    fi
elif [ "$REWARD_EXISTS" = "yes" ]; then
    REWARD=$(docker exec "$CONTAINER_NAME" cat /logs/verifier/reward.txt 2>/dev/null)
    if [ "$REWARD" = "1" ]; then
        PASSED="yes"
    else
        PASSED="no"
    fi
fi

# Cleanup
docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1

echo ""
if [ "$PASSED" = "yes" ]; then
    echo "ORACLE VALIDATION: PASSED ✓"
    echo "  - Docker build:  OK"
    echo "  - solve.sh:      exit code $SOLVE_EXIT"
    echo "  - test.sh:       exit code $TEST_EXIT"
    echo "  - Result:        ALL TESTS PASSED"
    exit 0
else
    echo "ORACLE VALIDATION: FAILED ✗"
    echo "  - test.sh exit:  $TEST_EXIT"
    echo "  - ctrf.json:     $CTRF_EXISTS"
    echo "  - reward.txt:    $REWARD_EXISTS"
    echo ""
    echo "Debug: docker run -it $IMAGE_NAME bash"
    exit 1
fi
