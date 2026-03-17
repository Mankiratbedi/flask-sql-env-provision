---
description: AmbiguityLabs tbench — guidelines for reviewing submitted tasks
globs: "**/instruction.md,**/task.toml,**/Dockerfile,**/test.sh,**/solve.sh,**/environment/**,**/solution/**,**/tests/**"
alwaysApply: false
---

# AmbiguityLabs tbench — Review Guidelines

Guidelines for reviewing tasks in the AmbiguityLabs tbench benchmark.

## Review Philosophy

As a reviewer, you're ensuring quality for the benchmark. Your goal is to:

- Catch issues before they enter the dataset
- Help contributors improve their tasks
- Maintain consistency across submissions
- Ensure tasks genuinely challenge LLM agents

---

## Review Checklist

### 1. Read the Task Description (instruction.md)

- Instruction reads like a senior engineer speaking to a peer — no LLM-isms, no emojis
- Concise: 1–2 paragraphs for problem description, reasonable number of requirements
- Requirements are clear and unambiguous
- All constraints are explicitly stated
- Absolute paths used throughout (e.g., `/app/code.py`)
- States the exact number of bugs (e.g., "exactly four bugs")
- States where the code lives (e.g., "at `/app/engine.py`")
- Says to make minimal fixes, not rewrite from scratch
- Canary string present as HTML comment (`<!-- CANARY-0x... -->`)

**Think like a malicious agent:** Does the description give extra information that makes cheating easier?

### 2. Review Tests (test_state.py)

- Every bug has 3+ corresponding tests (boundary, normal, edge)
- 5+ integration tests that require ALL bugs fixed
- Tests have informative docstrings
- Tests verify behavior, not implementation
- No brittle string matching
- Canary string in module docstring
- File is named `test_state.py` (not test_outputs.py)
- Imports from `/app` using `sys.path.insert(0, "/app")`
- Reference implementations in tests compute expected values independently

### 3. Check test.sh

- Writes reward to `/logs/verifier/reward.txt` on both pass (`1`) and fail (`0`)
- Uses `pytest-json-ctrf==0.3.5` (not `pytest-ctrf`)
- Is executable (`chmod +x`)
- Canary string present as comment
- Creates `/logs/verifier/` directory before writing

### 4. Check Solution (solve.sh)

- Starts with `#!/bin/bash` and `set -euo pipefail`
- Uses Python string replacement (`code.replace(...)`) — not fragile sed
- Each replacement targets a unique string (including bug comments)
- Is executable (`chmod +x`)
- Canary string present as comment
- Oracle test scores 1.000: `harbor run --agent oracle --path tasks/<name>`

### 5. Check Environment (Dockerfile)

- Builds successfully (no version-pinned apt packages)
- Buggy code embedded via heredoc (`RUN cat > /app/file.py << 'EOF'`)
- Does NOT contain solution or test files
- Base image is appropriate (`python:3.12-slim` for Python tasks)
- `WORKDIR /app`
- Canary string present as comment

### 6. Verify Metadata (task.toml)

- `version = "1.0"` — string, not float
- `author_name = "AmbiguityLabs"`
- `author_email = "hello@ambiguitylabs.in"`
- All sections present: `[metadata]`, `[verifier]`, `[agent]`, `[environment]`
- `difficulty` matches actual task complexity
- `category` and `tags` match actual content
- Canary string present as comment at top

### 7. Run Validation

- Oracle passes: `harbor run --agent oracle --path tasks/<name>` → Mean: 1.000
- NOP fails: `harbor run --agent nop --path tasks/<name>` → Mean: 0.000
- No Docker build errors
- No `RewardFileNotFoundError`

### 8. Bug Design Quality

- 4+ bugs for hard/expert tasks
- Bugs are syntactically valid — code runs, just produces wrong results
- Bugs require understanding the codebase, not surface-level fixes
- At least 2 bugs interact (fixing one changes another's behavior)
- Bugs exploit LLM weaknesses: precise computation, execution tracing, inverted conditions, off-by-one, missing operations, swapped operands

---

## Common Issues to Flag

### Task Description Problems

| Issue | Example |
|-------|---------|
| Ambiguous requirements | "Fix the issues" without stating how many |
| Missing output specs | Tests check files not mentioned in instruction |
| Relative paths | `./data/file.txt` instead of `/app/data/file.txt` |
| Step-by-step hints | Telling the agent exactly how to fix each bug |
| LLM-isms | "You are an expert...", "Certainly!" |

### Test Problems

| Issue | Example |
|-------|---------|
| Tests pass without fixes | NOP scores > 0.0 |
| Missing coverage | Bug has no dedicated test |
| Brittle matching | Exact string comparison where semantic check would suffice |
| Leaked answers | Expected values visible in test names or assertion messages |
| Implementation testing | Parsing source code instead of testing behavior |

### Solution Problems

| Issue | Example |
|-------|---------|
| Hardcoded answers | `echo "42" > result.txt` |
| Non-unique replacement | `code.replace("return x", ...)` matches multiple locations |
| Fragile sed | `sed -i 's/old/new/'` breaks on special characters |
| Oracle fails | solve.sh doesn't fix all bugs |
| Missing `set -euo pipefail` | Silent failures not caught |

### Environment Problems

| Issue | Example |
|-------|---------|
| Pinned apt version | `git=1:2.39.*` fails on newer base images |
| Solution leaked | Expected output file baked into Dockerfile |
| Wrong package name | `pytest-ctrf` instead of `pytest-json-ctrf` |
| Version as float | `version = 1.0` instead of `version = "1.0"` |
| Missing reward file | test.sh doesn't write `/logs/verifier/reward.txt` |

---

## Anti-Cheating Considerations

Think about how agents could cheat:

- Read bug comments to find fixes without understanding the code
- Replace the entire file with a rewritten version (instruction says "minimal fixes")
- Hardcode test outputs instead of actually fixing bugs
- Modify test files or data files
- Use known patterns from training data (canary strings help prevent this)

---

## Review Actions

| Action | When |
|--------|------|
| **Approve** | Task passes oracle (1.000) and nop (0.000). All HIGH criteria met. |
| **Approve with Note** | Single MEDIUM issue. Document it. |
| **Request Changes** | HIGH or multiple MEDIUM failures. Be specific: *what's wrong*, *where*, *how to fix*. |
| **Reject** | Fundamental issues: too easy, duplicate concept, core design flawed. Explain clearly. |

### Feedback Quality

**Good feedback:**

> Bug 3 (lazy quantifier) in test_state.py line 68 — the test `test_lazy_star` passes even without fixing bug 3 because the greedy path also matches. Add a test where lazy and greedy produce different results (e.g., `<.+?>` vs `<.+>` on `<a><b>`).

**Bad feedback:**

> Tests need work.
