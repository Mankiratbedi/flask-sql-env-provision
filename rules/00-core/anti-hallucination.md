# 00-core — Anti-hallucination

**Scope:** Applies to every action (create, edit, audit, review, package, claim-of-done).

Behave like a strict Terminus reviewer first and a code generator second. Verify real files before making claims. Never invent files, CI results, agent pass rates, rubric quality, reviewer decisions, or platform feedback.

## Evidence rules (hard)

- **Inspect first, claim second.** Before saying any file exists, list the actual directory. Before saying any field is set, read it. Before saying a test passed, run it.
- **No invented files.** Do not reference `solve.sh`, `test.sh`, `task.toml`, milestone folders, wheels, or any path unless verified to exist.
- **No invented CI outcomes.** Do not say "should pass CI", "CI-clean", "ready", "accepted", "passing", or "verified" without local oracle + verifier runs *or* explicit platform evidence (logs, screenshots, reviewer comment).
- **No invented difficulty.** Without agent-run data, label difficulty as **target**, not confirmed.
- **No invented codebase size.** Count meaningful files in `environment/` (excluding `Dockerfile`, `docker-compose*`). Apply [task-toml.md](../10-task-shape/task-toml.md) thresholds. Never pad with filler.
- **No invented dependencies.** Only pin what is actually used. No random packages, no placeholder versions.
- **No invented schemas.** If a test enforces a JSON/CSV/CLI/API/DB shape, that shape must be explicit in `instruction.md` or in a doc the instruction links to.
- **No invented coverage.** Every test maps to an instruction requirement; every instruction requirement maps to at least one test. Audit both directions.
- **No invented anti-cheat.** Anti-cheat = mutated fixtures, recomputed expected values, behavior tests, DB-state checks. Not file-existence assertions.
- **No invented rubric quality.** Rubrics are authored in the platform UI, never as a file. Lines must be task-specific and **trace-evidenced** — confirmable from the agent's trace, not "Agent understands the task" filler. Emit one `#Rubric N` block per milestone; each line starts `Agent`, ends `, +N`/`, -N`; scores ∈ ±1/2/3/5 (**never 4**); ≥5 checks with ≥3 negatives; positives sum 10–40 (aim ~10–20) per milestone. See [../40-workflow/rubric.md](../40-workflow/rubric.md).
- **No synthetic feel.** The submission must read as human-authored: no boilerplate comments, no over-structured markdown, no generated padding to inflate `codebase_size` or fake `long_context`. Every file must serve a real purpose in the codebase.
- **No silent guesses.** When unsure between two readings, choose the stricter rule and leave a short note.

## Mandatory self-check before declaring done

Output this list with **real evidence** before saying any task is ready:

- Task type — milestone or non-milestone (confirm against actual folder layout).
- Languages actually used.
- `codebase_size` and the file count that justifies it.
- Category and subcategories.
- Root structure found (`ls -la` the task dir).
- For milestones: every `steps/milestone_N/` folder listed.
- `task.toml` required fields read field-by-field.
- Dockerfile dependency pins read line-by-line.
- `instruction.md` paths grep'd for absolute-path compliance.
- `instruction.md` audited against the six principles (see [instruction-md.md](../10-task-shape/instruction-md.md)).
- Tests mapped to instruction requirements (both directions).
- `test.sh` reward tail matches the canonical block byte-for-byte (see [test-sh.md](../30-tests/test-sh.md)).
- Oracle script reviewed for determinism, no web/package downloads.
- `environment/` scanned for solution / ground-truth / hidden hints / expected outputs.
- Rubric authored in the platform UI (not a file); trace-evidenced; one `#Rubric N` block per milestone; each line starts `Agent`, ends `, +N`/`, -N`; scores ±1/2/3/5 (never 4); ≥5 checks with ≥3 negatives; positives sum 10–40 (aim ~10–20).
- No canary strings anywhere; no stray root files (`rubric.*`, `difficulty-check-summary.md`, `.ruff_cache/`).
- Declared `difficulty` matches actual agent pass rates if platform data exists.
- Local oracle + verifier commands actually run, or stated explicitly as **not run**.

If any item cannot be verified, **do not** mark the task ready.

## Language to use vs. avoid

| Use | Avoid |
|---|---|
| "I read `task.toml` — `allow_internet = false` is set on line 14." | "task.toml looks good." |
| "Not verified yet — oracle has not been run." | "Should pass CI." |
| "Target difficulty: hard (no agent data)." | "Confirmed hard." |
| "Codebase size 47 files; qualifies as `small`." | "Codebase is appropriately sized." |

## Pre-submit anti-hallucination tail

Right before zipping, re-run the full self-check. If any answer changed since the last run, **fix and re-check** — do not zip a task whose state you stated incorrectly five minutes ago.
