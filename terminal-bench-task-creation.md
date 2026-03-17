---
description: tbench (Harbor Framework) — task creation guidelines, workflow, validation for AmbiguityLabs
alwaysApply: true
---

# tbench — AmbiguityLabs Task Creation Guide

## Before Writing Any Code — Gather Required Information

When a user wants to create a new task, ALWAYS ask for ALL missing required fields BEFORE writing any code — even if the user already provided some information (like the problem statement or category). Check what's been given and ask for anything still missing.

**Required fields (MUST ask if not provided):**
1. **Task Idea**: What should the task accomplish? What problem should the agent solve?
2. **Programming Language**: What language(s) will the solution primarily use? (Python, Bash, C, etc.)
3. **Difficulty Level**: easy, medium, hard, or expert — ALWAYS ask, never assume
4. **Category**: Ask user to choose from:
   - programming
   - systems
   - cryptography
   - data-engineering
   - devops
   - networking
   - compilers
   - debugging
   - security
   - scientific-computing
5. **Task Name**: A kebab-case name for the task directory (e.g., broken-regex-engine)

**Optional fields (ask if relevant):**
6. **Tags**: Descriptive tags for the task (e.g., `["regex", "backtracking", "debugging"]`)

### Fixed Values (Do Not Ask)
- **Author Name**: Set to `AmbiguityLabs`
- **Author Email**: Set to `hello@ambiguitylabs.in`
- **Version**: Always `"3.0"`

### CRITICAL: Even if the user provides a problem statement and category, you MUST still ask for difficulty level and task name before writing any code. Do NOT guess or use defaults for these fields.

## Workflow

### 1. Setup
```bash
cd /path/to/your/project
uv tool install harbor
docker ps  # verify Docker is running
```

### 2. Create Task Directory
```bash
mkdir -p tasks/<task-name>/{environment,solution,tests}
```

### 3. Build — Fill in all files (see File Rules below)

### 4. Test Locally
```bash
# Oracle test — MUST score 1.000
harbor run --agent oracle --path tasks/<task-name>

# NOP test — MUST score 0.000
harbor run --agent nop --path tasks/<task-name>
```

### 5. Debug (if tests fail)
Check the job output directory for logs:
```bash
# Find latest job directory
ls -la jobs/

# Check test output
cat jobs/<latest>/*/verifier/test-stdout.txt

# Check exceptions
cat jobs/<latest>/*/exception.txt

# Check trial log
cat jobs/<latest>/*/trial.log
```

## Task Structure

```
tasks/<task-name>/
├── instruction.md          # Task instruction for the agent
├── task.toml               # Configuration and metadata
├── environment/
│   └── Dockerfile          # Container environment setup (includes buggy code)
├── solution/
│   └── solve.sh            # Reference solution (Oracle)
└── tests/
    ├── test.sh             # Test runner script
    └── test_state.py       # Pytest verification tests
```

## Canary String

Every task MUST include a unique canary string in ALL task files (task.toml, Dockerfile, solve.sh, test_state.py, instruction.md). This prevents dataset contamination.

Format: `CANARY-0x<HEX>-<task-name>` (e.g., `CANARY-0x7F3A9B2C-regex-engine`)

Generate a unique hex value for each task.

## File Rules

### task.toml

```toml
# CANARY-0xABCD1234-task-name
version = "1.0"

[metadata]
author_name = "AmbiguityLabs"
author_email = "hello@ambiguitylabs.in"
difficulty = "hard"
category = "programming"
tags = ["tag1", "tag2", "tag3"]

[verifier]
timeout_sec = 120.0

[agent]
timeout_sec = 600.0

[environment]
build_timeout_sec = 600.0
cpus = 2
memory_mb = 2048
storage_mb = 10240
gpus = 0
```

**Critical**: `version` MUST be a string (`"1.0"`), NOT a number (`1.0`). Harbor's Pydantic model validation will reject a float.

### instruction.md

```markdown
# Task Title

<!-- CANARY-0xABCD1234-task-name -->

Problem description: 1-2 paragraphs stating what's broken and what the agent must do.

- Tone: senior engineer speaking to a peer — concise, technical
- Use absolute paths (`/app/output.txt`, never `./output.txt`)
- List ALL expected output files the tests will check
- Don't enumerate step-by-step procedures — state the goal
- Don't give excessive hints on how to solve it
- No LLM-isms ("You are an expert...", "Certainly!")
- Mention how many bugs/issues exist (e.g., "exactly four bugs")
- Say where the code lives (e.g., "at `/app/engine.py`")
- Say to make minimal fixes, not rewrite from scratch
```

### Dockerfile

The Dockerfile creates the broken environment. It embeds the buggy code directly.

```dockerfile
FROM python:3.12-slim
# CANARY-0xABCD1234-task-name

RUN pip install --no-cache-dir uv
RUN mkdir -p /app
WORKDIR /app

# Write buggy code into the container using heredoc
RUN cat > /app/buggy_code.py << 'PYEOF'
#!/usr/bin/env python3
# ... buggy code here ...
PYEOF
```

**Rules:**
- NEVER copy solution/ or tests/ into the container
- NEVER pin apt versions (e.g., `git=1:2.39.*`) — use unversioned (`git`)
- NEVER install test dependencies in the Dockerfile
- Always: `apt-get update && apt-get install -y ... && rm -rf /var/lib/apt/lists/*`
- Embed buggy code via `RUN cat > /app/file.py << 'EOF'` heredocs
- Include the canary string as a comment near the top
- For data generation, use `RUN python3 << 'GENEOF'` blocks

### solve.sh

The oracle solution — must fix ALL bugs and pass ALL tests.

```bash
#!/bin/bash
set -euo pipefail
# CANARY-0xABCD1234-task-name

cd /app

python3 << 'PATCH'
code = open("buggy_code.py").read()

# Fix each bug using exact string replacement
code = code.replace(
    "buggy line of code",
    "fixed line of code"
)

open("buggy_code.py", "w").write(code)
PATCH

echo "All bugs fixed."
```

**Rules:**
- Must pass ALL tests when run inside the container
- Use Python string replacement for surgical fixes (not sed — too fragile)
- Match exact strings including comments/whitespace for unique replacement targets
- Include the canary string
- Must be executable: `chmod +x solution/solve.sh`

### test.sh

This script runs pytest and writes the reward file.

```bash
#!/bin/bash
# CANARY-0xABCD1234-task-name

mkdir -p /logs/verifier

uvx \
  --with pytest==8.4.1 \
  --with pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_state.py -rA 2>&1

RESULT=$?

if [ $RESULT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
```

**Critical:**
- Must write `1` or `0` to `/logs/verifier/reward.txt`
- Without this file, Harbor raises `RewardFileNotFoundError`
- Use `uvx` to install pytest at runtime (not in Dockerfile)
- `pytest-json-ctrf==0.3.5` is the correct package name (NOT `pytest-ctrf`)
- Must be executable: `chmod +x tests/test.sh`

### test_state.py

```python
"""Tests for the task — all bugs must be fixed to pass.

CANARY-0xABCD1234-task-name
"""
import sys
sys.path.insert(0, "/app")
from buggy_code import some_function

# One test per bug, plus integration tests
def test_bug_1_description():
    """Clear docstring explaining what this tests."""
    assert some_function() == expected_result

# ... more tests ...
```

**Rules:**
- File MUST be named `test_state.py`
- Include canary string in module docstring
- One or more tests per bug — tests should FAIL without the fix
- Add integration/regression tests that verify overall correctness
- Informative docstrings on every test function
- Make it hard for agents to cheat
- Import from `/app` using `sys.path.insert(0, "/app")`

## Bug Design Principles — Making Tasks That LLMs Fail

### What makes LLMs fail:
1. **Precise computation**: Byte-level operations, hash values, exact offsets
2. **Execution tracing**: Bugs only visible by mentally running the code
3. **Interacting bugs**: Fix A reveals bug B; bugs mask each other
4. **Inverted conditions**: `<` vs `<=`, `and` vs `or`, `is_alloc` vs `not is_alloc`
5. **Off-by-one errors**: Footer offsets, jump targets, sequence numbers
6. **Missing operations**: A line that should exist but doesn't (e.g., missing restore)
7. **Swapped operands**: `a/b` vs `b/a`, `left+right` vs `right+left`

### Bug planting strategy:
- Plant 4-5 bugs per task (not 1-2, which is too easy)
- Include BUG comments in the code — these serve as replacement anchors for solve.sh
- Make bugs syntactically valid — code compiles/runs, just produces wrong results
- Ensure doing nothing (nop) fails ALL tests, not just some
- Each bug should be independently testable via specific test cases
- At least 2 bugs should interact (fixing one makes another's symptoms change)

### Test design:
- 3-5 tests per bug (boundary cases, normal cases, edge cases)
- 5-10 integration tests that require ALL bugs fixed
- Reference implementation in tests (compute expected values independently)
- Don't leak answers in test names or assertion messages

## Task Difficulty Guidelines

| Difficulty | Bugs | Code Size | Domain Knowledge | Expected LLM Score |
|-----------|------|-----------|------------------|-------------------|
| easy      | 1-2  | <100 lines | Basic programming | 0.7-1.0 |
| medium    | 2-3  | 100-250 lines | Intermediate CS concepts | 0.3-0.7 |
| hard      | 3-4  | 200-400 lines | Professional domain expertise | 0.0-0.3 |
| expert    | 4-5  | 300-500 lines | Deep systems/theory knowledge | 0.0 |

## Validation Commands

```bash
# Oracle test — MUST score 1.000
harbor run --agent oracle --path tasks/<task-name>

# NOP test — MUST score 0.000
harbor run --agent nop --path tasks/<task-name>

# Debug failing tests
cat jobs/<latest-job>/<task>__*/verifier/test-stdout.txt
cat jobs/<latest-job>/<task>__*/exception.txt
```

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ValidationError: version Input should be a valid string` | `version = 1.0` (float) | Use `version = "1.0"` (string) |
| `RewardFileNotFoundError` | test.sh doesn't write reward.txt | Add reward block to test.sh |
| `pytest-ctrf was not found` | Wrong package name | Use `pytest-json-ctrf==0.3.5` |
| `Package git version not found` | Pinned apt version | Remove version pin: `git` not `git=1:2.39.*` |
| `Docker compose command failed` | Dockerfile build error | Check Dockerfile syntax, remove version pins |
| Tests pass without solve.sh | Tests don't actually verify bug presence | Make tests that specifically expose each bug |

## PR Checklist

- [ ] All behavior in tests is described in instruction.md
- [ ] All behavior in instruction.md is checked in tests
- [ ] Test cases have informative docstrings
- [ ] Hard for agent to cheat
- [ ] instruction.md has senior engineer tone (no LLM-isms)
- [ ] Canary string present in ALL files
- [ ] `version = "1.0"` (string, not float)
- [ ] test.sh writes `/logs/verifier/reward.txt`
- [ ] solve.sh is executable (`chmod +x`)
- [ ] test.sh is executable (`chmod +x`)
- [ ] Oracle passes (reward = 1.0)
- [ ] NOP fails (reward = 0.0)
- [ ] No apt version pins in Dockerfile
- [ ] No test dependencies in Dockerfile
- [ ] `author_name = "AmbiguityLabs"`

## Key Reminders
- NEVER share API keys in chat, code, or messages
- author_name = "AmbiguityLabs", author_email = "hello@ambiguitylabs.in"
- version = "1.0" (string, always)
- Test file = `test_state.py` (not test_outputs.py)
- Quality over quantity — tasks must pass both oracle AND nop
- Prefer single-container Docker setups
- Embed buggy code in Dockerfile via heredocs
- Use Python string replacement in solve.sh (not sed)
