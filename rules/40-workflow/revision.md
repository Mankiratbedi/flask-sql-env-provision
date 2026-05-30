# 40-workflow — Revision (reviewer feedback)

**Scope:** Fixing a task after reviewer feedback or after a failed CI / oracle / nop run.

## Principles

- **Inspect actual files before editing.** Don't assume what's there.
- **Map each reviewer comment to specific files.** No comment lives in the air — every one points at a path.
- **Fix only the reported issue and directly related blockers.** Don't rewrite working parts.
- **Don't add complexity** (extra services, dependencies, edge cases, "while I'm here" refactors) unless required.
- **Keep instruction concise.** Don't bloat in response to a "more detail" comment — link to a contract doc instead.
- **Keep tests aligned with instruction.** If you add a test, the instruction must require what it tests; if you remove a requirement, remove the test.
- **Keep the oracle deterministic and scoped.** A revision is not an excuse to widen oracle scope.
- **Re-run the full quality gates** (ruff, abs-path, oracle, nop) after every revision — not just the parts you touched.

## Workflow

### 1. Read every reviewer comment

Write down each comment, mapped to the file(s) it concerns. Don't start editing until the map is complete.

```
Comment 1: "instruction says /app/output but tests look at /out"
  → instruction.md (line ~N) OR tests/test_outputs.py (line ~N) — pick the right one to change

Comment 2: "oracle hardcodes the answer"
  → solution/solve.sh / solveN.sh

Comment 3: "missing memory_mb in task.toml"
  → task.toml [environment]
```

### 2. Apply minimal, targeted fixes

One edit per comment when possible. Re-read the file after each edit to confirm the change landed.

### 3. Re-run the full pre-submit checklist

Even if your fix touched only `instruction.md`, run [pre-submit-checklist.md](pre-submit-checklist.md) end-to-end. A path change in `instruction.md` cascades through `test.sh`, `solve.sh`, and `Dockerfile`.

### 4. Report

After the revision, output:

- **Reviewer issue:** quote the comment.
- **Files changed:** list with line ranges.
- **Exact change:** what was added / removed / replaced.
- **Verification:** which checks were run and their outcomes.
- **Status:** `verified` (gates 1–4 passed locally) or `not verified yet` (state which gate didn't run).

Never claim `verified` without actually running gates 1–4.

## Common revision patterns

### "Instruction is missing X / not specific enough"

- First check whether tests verify X. If yes → either add the requirement to `instruction.md` (concisely, or via the contract doc) or remove the test.
- Don't dump a paragraph into `instruction.md`. Add a one-line requirement or a link to `/app/docs/<contract>.md`.

### "Tests don't cover Y"

- Confirm Y is in `instruction.md`. If not, add it (concisely) before adding the test.
- Write the test to assert behavior, not file existence (see [../30-tests/oracle-nop-contract.md](../30-tests/oracle-nop-contract.md)).
- Re-run NOP — the new test must fail under NOP.

### "Oracle hardcodes the answer"

- Replace `echo '{...}' > /app/output` with code that computes the answer from the inputs.
- Re-run oracle — must still return `1`.
- Re-run NOP — must still return `0`.

### "task.toml field missing / out of range"

- Add the missing field with a justified value (see [../10-task-shape/task-toml.md](../10-task-shape/task-toml.md)).
- If `agent.timeout_sec` was over 1800, trim scope rather than fighting the cap.

### "Path mismatch"

- Pick the canonical path (usually whatever `instruction.md` says — that's the user contract).
- `grep -RIn '<old-path>' tasks/<task-name>/` and replace everywhere.
- Re-run oracle to confirm.

### "Codebase size doesn't match `codebase_size`"

- Count `environment/` files excluding `Dockerfile` and `docker-compose*`.
- Adjust `codebase_size` to match the actual count's bracket.
- Never pad with filler files to clear a threshold.

### "Test leaks the answer"

- A test like `assert output == EXPECTED_VALUE` where `EXPECTED_VALUE` is hardcoded leaks the answer to anyone reading the test file.
- Compute the expected value inside the test from the (mutated) inputs.
- Confirm a fresh oracle still produces the same answer after the test recomputes it.

## When NOT to revise

If the reviewer comment conflicts with these rules (00-core specifically) or with a memory entry, raise the conflict with the user instead of silently violating the rules. Stricter rule wins. See [../index.md](../index.md) — conflict resolution.
