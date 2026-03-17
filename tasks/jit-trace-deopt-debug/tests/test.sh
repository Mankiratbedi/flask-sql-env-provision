#!/bin/bash
# CANARY-0x4A2F8E91-jit-trace-deopt-debug

mkdir -p /logs/verifier

# Run pytest using the system-installed package
python3 -m pytest --ctrf /logs/verifier/ctrf.json /tests/test_state.py -rA 2>&1

RESULT=$?

if [ $RESULT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
