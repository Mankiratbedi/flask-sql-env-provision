# 40-workflow — Pre-Submit Checklist

**Scope:** The ordered, runnable check sequence before any `tasksubmit/<task-name>.zip` is built.

This is **not** prose to skim. Execute top-down. Fix the first failure before moving on. Do not jump ahead.

## 0. Sanity — task tree exists where expected

```bash
ls -la tasks/<task-name>/
```

- Flat: `instruction.md`, `task.toml`, `environment/`, `solution/`, `tests/` at task root.
- Milestone: `task.toml`, `environment/`, `steps/milestone_N/` (no root `instruction.md` / `tests/` / `solution/`).

If wrong layout → fix per [../10-task-shape/layout.md](../10-task-shape/layout.md). Do not continue.

## 1. `task.toml` audit

```bash
python3 -c "import tomllib; d=tomllib.loads(open('tasks/<task-name>/task.toml','rb').read().decode()); print(d)"
```

Confirm against [../10-task-shape/task-toml.md](../10-task-shape/task-toml.md):

- [ ] `version = "2.0"`
- [ ] `agent.timeout_sec ≤ 1800.0` (every `[agent]` and `[steps.agent]`)
- [ ] `environment.allow_internet = false`
- [ ] `difficulty ∈ {"medium", "hard"}`
- [ ] `codebase_size ∈ {"small", "large"}` (no `minimal`)
- [ ] `number_of_milestones` matches `[[steps]]` count exactly
- [ ] `memory_mb`, `storage_mb`, `cpus`, `build_timeout_sec` all present
- [ ] **no** `workdir` on flat tasks (milestone-only field)
- [ ] Languages list does not include Python unless Python is primary
- [ ] `author_name` / `author_email` set and consistent across submissions
- [ ] each `[[steps]]` block has a `name` (milestone tasks); flat tasks need no top-level `name`

## 2. `instruction.md` audit

For each `instruction.md` (root for flat, each milestone for milestone):

```bash
wc -w tasks/<task-name>/instruction.md
grep -nE '(^|[^/])(\./|\.\./)' tasks/<task-name>/instruction.md || echo "OK: no relative paths"
grep -nE '(CANARY-|<task-name>)' tasks/<task-name>/instruction.md || echo "OK: no canary/task-name"
```

- [ ] Word count ≈ 100–250.
- [ ] All paths absolute (`/app/...`).
- [ ] No task name, no `CANARY-*` string.
- [ ] No stepwise solution guidance.
- [ ] Output paths match `test_outputs.py`, `Dockerfile`, `solve.sh` byte-for-byte.

See [../10-task-shape/instruction-md.md](../10-task-shape/instruction-md.md).

## 3. **Gate 1 — Ruff clean**

```bash
ruff check tasks/<task-name>/tests/
ruff check tasks/<task-name>/steps/*/tests/        # milestone only
ruff check tasks/<task-name>/tests/verifier-tools/ # if present
```

Must return **no findings**. F401 and F841 are blockers. See [../30-tests/ruff-clean.md](../30-tests/ruff-clean.md).

## 4. **Gate 2 — Absolute-path scan**

```bash
# Search for relative paths in all task source files
grep -RnE '(^|[^/])(\./|\.\./)' \
    tasks/<task-name>/instruction.md \
    tasks/<task-name>/tests/ \
    tasks/<task-name>/environment/Dockerfile \
    tasks/<task-name>/solution/ \
    2>/dev/null || echo "OK: no relative paths"
```

Cross-file consistency:

```bash
# A path mentioned in instruction.md must appear identically elsewhere
grep -oE '/app/[A-Za-z0-9_./-]+' tasks/<task-name>/instruction.md | sort -u
# spot-check those paths appear in test_outputs.py, Dockerfile, solve.sh
```

## 5. `test.sh` reward-block check

```bash
tail -6 tasks/<task-name>/tests/test.sh
# milestone:
for f in tasks/<task-name>/steps/*/tests/test.sh; do echo "== $f =="; tail -6 "$f"; done
```

Confirm the file **ends with** the literal reward block the static checker
enforces — bare `$?`, 4-space indent, ending at `fi`, **nothing after**:

```bash
python3 -m pytest ... -rA
if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
```

- `set -uo pipefail` at the top (not `set -e`).
- pytest is the command immediately before the `if`, so `$?` is pytest's exit.
- **No** `RC=$?`, **no** `exit "$RC"` after `fi` — the static checker rejects
  those with `❌ Must end with the reward section`.

See [../30-tests/test-sh.md](../30-tests/test-sh.md).

## 6. Verifier-deps check (isolated venv, not system Python)

```bash
# Test deps must go in an isolated /opt/verifier-venv, NOT the system Python or wheels in tests/
grep -nE 'verifier-venv|python3-venv' tasks/<task-name>/environment/Dockerfile   # should show venv build
grep -nE 'break-system-packages' tasks/<task-name>/environment/Dockerfile        # MUST return nothing
find tasks/<task-name> -name '*.whl' -o -name 'wheels' -type d                   # must return nothing
grep -RnE 'pip install|python -m venv|python3 -m venv' tasks/<task-name>/tests/ tasks/<task-name>/steps/*/tests/ 2>/dev/null  # must return nothing
# After build, the SYSTEM python must NOT import the test deps:
# docker run --rm <img> python3 -c "import pytest" 2>&1 | grep -q "No module" && echo OK
```

- [ ] `environment/Dockerfile` builds `/opt/verifier-venv` and installs test deps there (pinned); `python3-venv` in apt.
- [ ] Test deps are **not** in the system/app Python (no `--break-system-packages`); `test_deps_in_image` passes.
- [ ] No `.whl` files and no `wheels/` directory anywhere under `tests/`.
- [ ] `test.sh` runs `/opt/verifier-venv/bin/python -m pytest` — no `pip install`, no venv creation at test time.
- [ ] No verifier-deps comment in `task.toml`.
- [ ] `.dockerignore` excludes `tests/` and `solution/`.

See [../20-environment/verifier-deps.md](../20-environment/verifier-deps.md).

## 7. Environment hygiene — no answer leakage

```bash
# These should all return nothing
grep -RInE '\b(BUG|FIXME|HACK|XXX)\b' tasks/<task-name>/environment/
grep -RInE 'TODO.*(solution|fix|bug)|fix (this|me|the bug)|the (bug|issue) is' tasks/<task-name>/environment/
ls tasks/<task-name>/environment/*expected*.* 2>/dev/null
ls tasks/<task-name>/environment/*answer*.* 2>/dev/null
ls tasks/<task-name>/environment/solution* 2>/dev/null
ls tasks/<task-name>/environment/test* 2>/dev/null
```

No hidden hints, no expected outputs, no solution files, no test files in `environment/`. Comments that name the bug, label the fix location, or walk through the intended solution are answer leakage — rewrite or remove them. Docs under `environment/` describe the system's API/contracts, never the task's solution.

## 7b. Submission cleanup — canary, junk, rubric files

```bash
# (a) No canary strings ANYWHERE in the submission (report blocker)
grep -RIn 'CANARY-' tasks/<task-name>/ || echo "OK: no CANARY- strings"
grep -RIn 'BENCHMARK DATA SHOULD NEVER APPEAR' tasks/<task-name>/ || echo "OK: no canary line"
grep -RIn 'canary GUID' tasks/<task-name>/ || echo "OK: no canary GUID line"

# (b) No stray files that don't belong in a task
find tasks/<task-name> \( -name 'rubric.md' -o -name 'rubric.txt' \
    -o -name 'difficulty-check-summary.md' -o -name '.ruff_cache' \
    -o -name '__pycache__' -o -name '.pytest_cache' \) -print
```

- [ ] No `CANARY-*`, no `BENCHMARK DATA...` line, no `# canary GUID:` anywhere.
- [ ] No `rubric.md` / `rubric.txt` (rubric is authored in the platform UI — see [repo-conventions.md](repo-conventions.md)).
- [ ] No `difficulty-check-summary.md`, `.ruff_cache/`, `.pytest_cache/`, `__pycache__/`.

## 7c. Rubric — emit in chat, author on the platform

The rubric is **not** a file. **Emit it in the chat as a ready-to-paste block** — one `#Rubric N` block per milestone — so the user can copy it into the submission UI. Every line starts `Agent`, names a **trace-evidenced** behavior, ends `, +N`/`, -N`; scores ∈ ±1/2/3/5 (never 4); ≥5 checks with ≥3 negatives; positives sum 10–40 (aim ~10–20) per milestone. See [rubric.md](rubric.md).

## 8. **Gate 3 — Oracle must pass**

```bash
harbor run -p tasks/<task-name> -a oracle \
    --job-name "oracle__<task>__$(date +%Y%m%d-%H%M%S)" -q
```

Confirm:

```bash
# Flat:
cat jobs/oracle__*/<task-name>__1/verifier/reward.txt  # must be 1
# Milestone:
for f in jobs/oracle__*/<task-name>__1/steps/*/verifier/reward.txt; do echo "$f:"; cat "$f"; done
```

Every `reward.txt` = `1`. Trial mean = `1.000`. If not, fix the task (not the test) and re-run. See [../30-tests/oracle-nop-contract.md](../30-tests/oracle-nop-contract.md).

## 9. **Gate 4 — NOP must fail**

```bash
harbor run -p tasks/<task-name> -a nop \
    --job-name "nop__<task>__$(date +%Y%m%d-%H%M%S)" -q
```

Every `reward.txt` = `0`. Trial mean = `0.000`. If NOP passes anywhere, tests are leaky — fix per [../30-tests/oracle-nop-contract.md](../30-tests/oracle-nop-contract.md).

## 10. Final self-check from anti-hallucination rules

Run the mandatory self-check from [../00-core/anti-hallucination.md](../00-core/anti-hallucination.md) — every item with real evidence (file contents, command output). If any answer is "not verified", do not zip.

## 11. Build zip (only after all above pass)

```bash
cd "tasks/<task-name>" && zip -r "../../tasksubmit/<task-name>.zip" . \
    -x "environment/target/*" \
    -x "**/__pycache__/*" \
    -x "**/*.pyc" \
    -x "**/.pytest_cache/*" \
    -x "**/.ruff_cache/*" \
    -x "rubric.md" -x "rubric.txt" \
    -x "difficulty-check-summary.md"
```

Verify flat root:

```bash
unzip -l tasksubmit/<task-name>.zip | head
# First non-directory entry MUST be task.toml (not <task-name>/task.toml)
```

See [repo-conventions.md](repo-conventions.md).

## 12. Mark ready

Now — and only now — the task is ready to ship. State the verification outputs (oracle/NOP reward, ruff result, zip filename), not just "done".
