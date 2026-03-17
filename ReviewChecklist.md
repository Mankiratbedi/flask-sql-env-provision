---
description: AmbiguityLabs tbench — task review checklist, severity guide, and section criteria
globs: "**/instruction.md,**/task.toml,**/Dockerfile,**/test.sh,**/solve.sh,**/environment/**,**/solution/**,**/tests/**"
alwaysApply: false
---

# AmbiguityLabs tbench — Task Review Checklist

## Severity Guide

| Severity | Meaning |
|----------|--------|
| **HIGH** | Any HIGH failure = task must be rejected. |
| **MEDIUM** | Multiple MEDIUM failures = reject. Single MEDIUM = accept with note. |
| **LOW** | LOW failures alone do not block acceptance. Include in revision notes if rejecting for other reasons. |

---

## 1. Instruction Prompt

| SEV | Criterion |
|-----|-----------|
| **HIGH** | Instruction is concise (1 sentence to 3 paragraphs). Reads like a senior engineer speaking to a peer — no emojis, minimal markdown. |
| **HIGH** | Goal is clear and well specified. Not primarily hard due to many unhandled edge cases. |
| **HIGH** | Task is interesting — useful to some group of developers or users. Represents real-world engineering challenges. |
| **HIGH** | No hints or step-by-step solve instructions in instruction.md. Requirements are OK, guidance is not. |
| **HIGH** | All referenced paths in the instruction use absolute references (e.g., `/app/code.py`). |
| **HIGH** | States the number of bugs/issues explicitly (e.g., "exactly four bugs"). |
| **HIGH** | States where the code lives (e.g., "at `/app/engine.py`"). |
| **MEDIUM** | Canary string present as HTML comment (`<!-- CANARY-0x... -->`). |
| **LOW** | Mentions "make minimal, targeted fixes — do not rewrite from scratch". |

*Notes:*

---

## 2. Environment (Dockerfile)

| SEV | Criterion |
|-----|-----------|
| **HIGH** | Dockerfile builds successfully (`harbor run` doesn't fail at build stage). |
| **HIGH** | No pinned apt versions (e.g., `git=1:2.39.*`). Use unversioned packages. |
| **HIGH** | Environment does not contain oracle solution or tests. Solution files only in `solution/`; test files only in `tests/`. |
| **HIGH** | Buggy code is embedded in the Dockerfile (via heredoc or COPY) — present in the container at runtime. |
| **HIGH** | Base image is appropriate (e.g., `python:3.12-slim` for Python tasks). |
| **MEDIUM** | Canary string present as comment near top of Dockerfile. |
| **MEDIUM** | Uses `WORKDIR /app` and code lives at `/app/`. |
| **LOW** | Cleans up apt lists: `rm -rf /var/lib/apt/lists/*`. |

*Notes:*

---

## 3. Oracle Solution (solve.sh)

| SEV | Criterion |
|-----|-----------|
| **HIGH** | Oracle passes consistently — `harbor run --agent oracle` scores 1.000. |
| **HIGH** | Oracle solves everything described in instruction.md — real fixes, not hardcoded test answers. |
| **HIGH** | Uses exact string replacement to fix bugs (unique match targets). |
| **HIGH** | solve.sh is executable (`chmod +x`). |
| **HIGH** | Starts with `#!/bin/bash` and `set -euo pipefail`. |
| **MEDIUM** | Uses Python string replacement (`code.replace(...)`) rather than fragile sed commands. |
| **MEDIUM** | Canary string present as comment. |
| **LOW** | Prints a confirmation message at the end (e.g., "All four bugs fixed."). |

*Notes:*

---

## 4. Verifiers (test.sh + test_state.py)

| SEV | Criterion |
|-----|-----------|
| **HIGH** | test.sh writes reward to `/logs/verifier/reward.txt` — both on pass (`1`) and fail (`0`). |
| **HIGH** | NOP test scores 0.000 — doing nothing fails ALL tests. |
| **HIGH** | test.sh is executable (`chmod +x`). |
| **HIGH** | Uses correct pytest package: `pytest-json-ctrf==0.3.5` (not `pytest-ctrf`). |
| **HIGH** | Test file is named `test_state.py`. |
| **HIGH** | All tests aligned to what is outlined in instruction.md — nothing tested that isn't defined. |
| **HIGH** | Verifiers check for actual correctness, not just format. |
| **HIGH** | Binary rewards only (`1` or `0`). No partial scores. |
| **MEDIUM** | 3+ tests per bug (boundary, normal, edge cases). |
| **MEDIUM** | 5+ integration/regression tests that require ALL bugs fixed. |
| **MEDIUM** | Canary string present in test_state.py docstring. |
| **LOW** | Informative docstrings on every test function. |

*Notes:*

---

## 5. Bug Design Quality

| SEV | Criterion |
|-----|-----------|
| **HIGH** | Each bug is independently testable — specific tests expose each bug. |
| **HIGH** | Bugs are syntactically valid — code compiles/runs, just produces wrong results. |
| **HIGH** | Bugs require understanding the codebase — not fixable by surface-level pattern matching. |
| **MEDIUM** | 4+ bugs for hard/expert difficulty tasks. |
| **MEDIUM** | At least 2 bugs interact (fixing one changes another's symptoms). |
| **MEDIUM** | Bug comments in code serve as unique replacement anchors for solve.sh. |
| **LOW** | Bugs exploit LLM weaknesses: precise computation, execution tracing, inverted conditions, off-by-one errors, missing operations. |

*Notes:*

---

## 6. Task Structure

| SEV | Criterion |
|-----|-----------|
| **HIGH** | All required files present: `environment/Dockerfile`, `solution/solve.sh`, `tests/test.sh`, `tests/test_state.py`, `instruction.md`, `task.toml`. |
| **HIGH** | Directory structure follows standard layout (no extra files at task root). |
| **LOW** | No unnecessary files (jobs/, README.md, __pycache__/). |

*Notes:*

---

## 7. Task Metadata (task.toml)

| SEV | Criterion |
|-----|-----------|
| **HIGH** | `version = "1.0"` — must be a string, not a float. |
| **HIGH** | All required sections present: `[metadata]`, `[verifier]`, `[agent]`, `[environment]`. |
| **HIGH** | `author_name = "AmbiguityLabs"` and `author_email = "hello@ambiguitylabs.in"`. |
| **MEDIUM** | `difficulty` matches actual task complexity (easy/medium/hard/expert). |
| **MEDIUM** | `tags` and `category` match actual task content. |
| **MEDIUM** | Canary string present as comment at top. |
| **LOW** | Reasonable timeout values (`verifier: 120s`, `agent: 600s`, `build: 600s`). |

*Notes:*

---

## Final Decision

| Option | When |
|--------|------|
| **APPROVE** | All criteria passed, or only LOW-severity issues found. |
| **APPROVE WITH NOTE** | Single MEDIUM-severity failure. Document the issue in notes below. |
| **REJECT** | Any HIGH-severity failure, or multiple MEDIUM-severity failures. |
| **REVISION** | Task needs fixes. Provide detailed feedback below. |

### Validation Results

| Test | Expected | Actual |
|------|----------|--------|
| `harbor run --agent oracle` | Mean: 1.000 | |
| `harbor run --agent nop` | Mean: 0.000 | |

*Feedback (if REVISION):*
