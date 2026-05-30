# 00-core — Quality Gates

**Scope:** Applies to every task before it is zipped to `tasksubmit/`.

These four checks are **blockers**. A task that fails any of them must not be packaged. Run them in this order — each cheaper than the next.

## Gate 1 — Ruff clean

Terminus CI runs `ruff check` over `tests/` and `tests/verifier-tools/`. **F401** (unused import) and **F841** (assigned-but-unused local) are **blocking errors**, not warnings.

```bash
ruff check tasks/<task-name>/tests/
# milestone tasks: also check each milestone's tests/ + any verifier-tools
ruff check tasks/<task-name>/steps/*/tests/
```

Audit `verifier-tools/*_ref.py` for leftover `import json` / debug captures. Audit test bodies for variables assigned and never read. See [ruff-clean.md](../30-tests/ruff-clean.md) for details.

## Gate 2 — Absolute-path scan

Every path in `instruction.md`, `test.sh`, `test_outputs.py`, `Dockerfile`, and `solve.sh` must be absolute (`/app/...`). Relative paths (`./foo`, `foo.txt`) are blockers.

```bash
# A useful one-liner pattern (adjust to your task)
grep -RnE '(^|[^/])\b(\./|\.\./)' tasks/<task-name>/instruction.md \
    tasks/<task-name>/tests/ tasks/<task-name>/environment/Dockerfile \
    tasks/<task-name>/solution/ || echo "OK: no relative paths"
```

Cross-check: a path mentioned in `instruction.md` must appear **identically** in `test_outputs.py`, `Dockerfile`, and `solve.sh`. Drift between files is the most common platform-side oracle failure.

## Gate 3 — Oracle must return reward = 1.0

The oracle (`solution/solve.sh` or per-milestone `solveN.sh`) must compute the answer and make the verifier write `1` to `/logs/verifier/reward.txt`.

```bash
# Flat task — works on harbor 0.1.45 and 0.8.0
harbor run -p tasks/<task-name> -a oracle \
    --job-name "oracle__<task>__$(date +%Y%m%d-%H%M%S)" -q

# Milestone task — needs harbor ≥ 0.8.0
harbor run -p tasks/<task-name> -a oracle \
    --job-name "oracle__<task>__$(date +%Y%m%d-%H%M%S)" -q
```

Look at `jobs/<job>/<task>__<trial>/.../verifier/reward.txt`. Must be `1`. For milestones, every step's `reward.txt` must be `1`. Trial-level mean lives in `result.json` under `stats.evals.oracle__adhoc.metrics[0].mean` — must be `1.000`.

**If oracle fails:** read job logs, diagnose root cause (path mismatch, missing dep, non-determinism, hidden hardcode), fix the task files, re-run. Do not "fix" by loosening tests.

## Gate 4 — NOP must return reward = 0.0

Without any solution, the verifier must write `0`. If NOP returns `1`, tests are too lenient (or the environment leaks the answer) — the task is broken.

```bash
harbor run -p tasks/<task-name> -a nop \
    --job-name "nop__<task>__$(date +%Y%m%d-%H%M%S)" -q
```

For milestones, every step's NOP `reward.txt` must be `0`. Mean must be `0.000`.

**If NOP passes (reward > 0):**
- Check for expected outputs left in `environment/` from a prior oracle run.
- Check for tests that only assert file existence (an empty `/app` may satisfy them).
- Check for tests that read agent-editable wrapper outputs whose default value happens to match.
- See [oracle-nop-contract.md](../30-tests/oracle-nop-contract.md).

## Gate order is not optional

Skipping ahead wastes time:

- Ruff catches typos and dead code in seconds.
- Path scan catches mismatches without Docker.
- Oracle reveals real environment / dependency bugs.
- NOP reveals leaky tests.

Run them top-down. Fix the first failure before moving on.

## Pre-zip gate

The pre-submit checklist ([../40-workflow/pre-submit-checklist.md](../40-workflow/pre-submit-checklist.md)) embeds these four gates as the first four steps. The zip command is the last step, never the first.

## Reference commands (memory)

Exact CLI for ruff / abs-path / oracle / nop is also pinned in memory under `reference_quality_gate_commands.md` — that file is the live source if anything below drifts.
