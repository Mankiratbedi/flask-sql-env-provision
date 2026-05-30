# CLAUDE.md — Project Terminus

> Claude-specific entry point. Read [`AGENTS.md`](AGENTS.md) for the editor-agnostic version; this file adds the bits specific to how Claude operates here (memory, tools, conventions).

## First thing — load the rules

At the start of every conversation in this repo, load **every** file under [`rules/`](rules/). The list and load order are in [`rules/index.md`](rules/index.md). These rules supersede the legacy `.cursor/rules/*.mdc` files; the archive is reference-only.

## Memory layer

Path: `~/.claude/projects/-home-adarsh-ambiguous-Project-Terminus/memory/`

The memory layer holds time-bounded overrides and durable pointers. It is loaded automatically into context at the start of every session. **When a memory entry conflicts with a rule under `rules/`, the newer entry wins** — memory tracks live corrections; `rules/` tracks the durable spec.

### Active memories (as of this writeup)

| Type | File | Purpose |
|---|---|---|
| feedback | `feedback_pin_cursor_rules.md` | Load all `.cursor/rules/*.mdc` (now superseded by `rules/`) at session start |
| feedback | `feedback_terse_comments.md` | 1–2 line comments only in committed task files; never cite rule filenames |
| feedback | `feedback_verifier_deps_in_dockerfile.md` | Install pytest/pytest-json-ctrf in the Dockerfile; tests/ holds only scripts (wheels in tests/ now a blocker) |
| feedback | `feedback_agent_timeout_cap.md` | CI rejects `agent.timeout_sec` > 1800 |
| feedback | `feedback_codebase_size_threshold.md` | small ≥ 20 env files; large ≥ 200 |
| feedback | `feedback_test_sh_reward_tail.md` | Canonical reward-tail block; literal-match lint |
| feedback | `feedback_zip_root_layout.md` | Zip to `tasksubmit/`, flat root |
| feedback | `feedback_ruff_clean_tests.md` | F401 / F841 are blockers in `tests/` and `verifier-tools/` |
| reference | `reference_harbor_milestone_cli.md` | Milestone tasks need harbor ≥ 0.8.0 |
| reference | `reference_quality_gate_commands.md` | Exact CLI for ruff / abs-path / oracle / nop |

Index file: `MEMORY.md` (the in-context summary).

### When to write to memory

- The user corrects an approach you took. Save the **rule**, the **why**, and **how to apply**.
- The user confirms a non-obvious choice worked. Save it the same way.
- You learn an external resource pointer (Linear project, Grafana board, etc.). Save as `reference_*`.

### When NOT to write to memory

- Anything already in `rules/` — write or update a rule file instead.
- Ephemeral task state (current PR, in-progress edit) — that's plan / todo territory.
- Code patterns derivable from the repo itself.

### When to refresh memory before acting

Memory entries are point-in-time observations. If a memory names a file path, function, or flag, **verify it still exists** before recommending or acting on it. If a memory describes "current state" of the repo, prefer `git log` / direct file reads over the snapshot.

## Tools and skills available in this repo

- `harbor` CLI (≥ 0.8.0 for milestone tasks).
- `ruff` for Python lint.
- `unzip`, `zip` for submission packaging.
- Standard Unix tooling (`grep`, `find`, `python3 -c "import tomllib"`).

There is no `Makefile` and no `scripts/` workflow in the current repo. Run harbor / ruff / zip commands directly.

## Conventions Claude should follow here

These supplement the rules in [`rules/`](rules/) with Claude-process specifics:

1. **Pin all `rules/*.md` at conversation start.** Don't selectively load a subset — the index lists every file for a reason.
2. **Quote evidence, don't paraphrase.** When claiming a fact about a task, cite the file and line. When claiming a verifier outcome, cite the path to `reward.txt`.
3. **Default to terse comments in committed task files** (1–2 lines max in `task.toml` / `test.sh` / `Dockerfile`). Never cite internal rule filenames in committed files.
4. **Never claim a task is "ready" or "passing" without showing the gates ran.** Use "verified" vs. "not verified yet" honestly.
5. **Prefer milestone tasks, non-Python languages, and no-tmux-as-subject** — these are the lanes that survive review.
6. **Emit the rubric in chat, ready to paste.** Rubrics live in the platform UI, never in a file — when you create or finalize a task, output the criteria as a copy-paste block (one per milestone). See [`rules/40-workflow/rubric.md`](rules/40-workflow/rubric.md).

## What Claude should NOT do here

- Re-create the retired `Makefile`, `scripts/`, or `ready_to_submit/` paths.
- Ship `.whl` files or a `wheels/` dir under `tests/` — verifier deps go in the Dockerfile (Edition 2).
- Add a `# canary GUID:` line or any `CANARY-*` string — canary is retired in Edition 2.
- Set `workdir` on a flat (non-milestone) task — it is a milestone-only field.
- Leave a `rubric.md` / `rubric.txt` in a task — rubrics are authored in the platform UI.
- Bump `agent.timeout_sec` above 1800 to "make the task fit" — trim scope instead.
- Skip a quality gate to ship faster — failed gates are real signals.
- Write multi-paragraph comments inside committed task files.
- Let `.cursor/rules/*.mdc` drift from `rules/`. The `.mdc` files are a maintained mirror (via the `.cursor/rules` → `cursor/.cursor/rules` symlink); when a rule changes, update **both** `rules/` and the matching `.mdc`. `rules/` stays canonical on any conflict.

## Where to look for things

| You need… | Look at… |
|---|---|
| Full task-authoring spec | [`rules/`](rules/) (start with [`rules/index.md`](rules/index.md)) |
| What lanes are accepted | [`rules/00-core/accepted-lanes.md`](rules/00-core/accepted-lanes.md) |
| Exact pre-zip checklist | [`rules/40-workflow/pre-submit-checklist.md`](rules/40-workflow/pre-submit-checklist.md) |
| Quality-gate CLI | [`rules/00-core/quality-gates.md`](rules/00-core/quality-gates.md) + memory `reference_quality_gate_commands.md` |
| Concrete task examples | [`rules/90-reference/accepted-patterns.md`](rules/90-reference/accepted-patterns.md) |
| Old deep spec (rarely needed) | [`.cursor/rules/terminus.mdc`](.cursor/rules/terminus.mdc) (archive) |
| Task ideas backlog | [`ideas.md`](ideas.md) |

## When in doubt

Stricter rule wins. If the rules are silent on a question, ask the user before guessing.
