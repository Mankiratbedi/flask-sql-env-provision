# Project Terminus — Rule Index

Entry point for all task-authoring rules in this repo. Load **every file listed below** at the start of any task work (create, revise, audit, package). On conflict between any two rules, prefer the **stricter** one.

These rules supersede the legacy `.cursor/rules/*.mdc` files (kept as archive in [90-reference/canonical-spec.md](90-reference/canonical-spec.md) — consult only when something below is silent).

## Hierarchy (load in this order)

### 00-core — non-negotiable
- [anti-hallucination.md](00-core/anti-hallucination.md) — verify before claim; never invent files, results, or status
- [accepted-lanes.md](00-core/accepted-lanes.md) — milestone-first, non-Python preferred, no-tmux-as-subject, avoid-list
- [quality-gates.md](00-core/quality-gates.md) — ruff, absolute-path scan, oracle pass, nop fail — all four are blockers

### 10-task-shape — what files exist and where
- [layout.md](10-task-shape/layout.md) — milestone vs non-milestone directory tree
- [instruction-md.md](10-task-shape/instruction-md.md) — six instruction principles, tone, absolute paths
- [task-toml.md](10-task-shape/task-toml.md) — required fields, `agent.timeout_sec ≤ 1800`, `codebase_size` thresholds

### 20-environment — container and runtime
- [dockerfile.md](20-environment/dockerfile.md) — base images, layers, tmux/asciinema requirement, verifier deps installed in image
- [runtime-verifier.md](20-environment/runtime-verifier.md) — `allow_internet = false`; no networked installs at runtime
- [verifier-deps.md](20-environment/verifier-deps.md) — install pytest/pytest-json-ctrf in the Dockerfile; no wheels in `tests/`

### 30-tests — test design and execution
- [test-sh.md](30-tests/test-sh.md) — file must END with the literal `if [ $? -eq 0 ]` reward block (4-space indent, ends at `fi`, no `RC=$?`/`exit`); `set -uo pipefail` (static-check enforced)
- [ruff-clean.md](30-tests/ruff-clean.md) — F401 / F841 are CI blockers in `tests/` and `tests/verifier-tools/`
- [oracle-nop-contract.md](30-tests/oracle-nop-contract.md) — oracle = 1.0, nop = 0.0; anti-cheat via mutation

### 40-workflow — this repo, this submission pipeline
- [repo-conventions.md](40-workflow/repo-conventions.md) — `tasks/<name>/`, `tasksubmit/` zips, harbor ≥ 0.8.0
- [rubric.md](40-workflow/rubric.md) — emit the rubric in chat, ready to paste into the platform UI (never a file)
- [pre-submit-checklist.md](40-workflow/pre-submit-checklist.md) — exact ordered checks before zipping
- [revision.md](40-workflow/revision.md) — reviewer feedback handling

### 90-reference — pointers only
- [accepted-patterns.md](90-reference/accepted-patterns.md) — concrete lane catalog with examples
- [canonical-spec.md](90-reference/canonical-spec.md) — archived `.cursor/rules/*.mdc` deep reference

## Scope marker

Every rule file declares its scope in the first lines. If a rule's scope does not match the work at hand, do not apply it. Test rules do not govern Dockerfiles; Dockerfile rules do not govern `instruction.md`.

## Conflict resolution

1. **00-core overrides everything else.**
2. Within the same tier, the stricter rule wins.
3. The memory layer at `~/.claude/projects/-home-adarsh-ambiguous-Project-Terminus/memory/` contains time-bounded overrides — they override these files when newer.
4. The archived `.cursor/rules/terminus.mdc` is reference-only; never apply a rule from there without confirming the split files don't already cover it.

## What this index does NOT contain

- User profile, project state, external pointers — those live in memory.
- Task content, ideas, code — those live in `tasks/<task-name>/` and `ideas.md`.
- Anything Cursor-IDE-specific — the `.cursor/rules/` tree is legacy and editor-bound; these `rules/*.md` files are editor-agnostic.
