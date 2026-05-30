# 40-workflow — Repo Conventions

**Scope:** Where files live in *this* repo, and how zips are built for submission.

## Directory layout (repo root)

```
Project-Terminus/
├── AGENTS.md                 # repo entry point for any AI agent
├── CLAUDE.md                 # Claude-specific entry; aliases AGENTS.md
├── rules/                    # ← these files (canonical task-authoring rules)
├── .cursor/rules/            # archived (legacy Cursor .mdc files)
├── ideas.md                  # task-idea backlog
├── tasks/                    # active task development
│   └── <task-name>/          # Harbor-format task directory
├── tasksubmit/                # zips ready for submission (THE drop directory)
│   └── <task-name>.zip
└── jobs/                     # harbor run output (gitignored)
```

There is no `ready_to_submit/` in this repo — that path was retired. Don't write zips there.

## Task development location

- Create and maintain every new task under **`tasks/<task-name>/`**.
- The live tree under `tasks/` is the source of truth; zips in `tasksubmit/` are produced from it.
- Never edit a zip directly. Never zip first and then patch.

## Submission zip — flat-root layout

The CI extracts the zip into a fixed `~/tasks/tbench-task/` directory and looks for `task.toml` and `tests/test.sh` **directly under that root**. The zip's first non-directory entry must be `task.toml`, not `<task-name>/task.toml`.

```bash
# Run from repo root. cd INTO the task dir, then zip its contents.
cd "tasks/<task-name>" && zip -r "../../tasksubmit/<task-name>.zip" . \
    -x "environment/target/*" \
    -x "**/__pycache__/*" \
    -x "**/*.pyc" \
    -x "**/.pytest_cache/*" \
    -x "**/.ruff_cache/*" \
    -x "rubric.md" -x "rubric.txt" \
    -x "difficulty-check-summary.md"
```

Verify:

```bash
unzip -l tasksubmit/<task-name>.zip | head
# First non-directory entry must be task.toml (not <task-name>/task.toml)
```

If you see a nested layout (`<task-name>/task.toml`), you zipped the folder instead of its contents — redo it from inside the task directory.

## Harbor CLI requirements

| Task type | Harbor version | Why |
|---|---|---|
| **Flat** (root `instruction.md`, `tests/`, `solution/`) | 0.1.45 **or** 0.8.0+ | Both support flat layout. |
| **Milestone** (`steps/milestone_N/`, `[[steps]]` blocks) | **0.8.0+** | Earlier versions only check root `instruction.md`/`tests/test.sh` and bail with `ValueError: Either datasets or tasks must be provided.` |

Upgrade: `uv tool upgrade harbor` (installed via `uv tool`; aliases `harbor`, `hb`, `hr`).

### Standard run commands

```bash
# Oracle
harbor run -p tasks/<task-name> -a oracle \
    --job-name "oracle__<task>__$(date +%Y%m%d-%H%M%S)" -q

# NOP
harbor run -p tasks/<task-name> -a nop \
    --job-name "nop__<task>__$(date +%Y%m%d-%H%M%S)" -q
```

Per-step reward (milestones): `jobs/<job>/<task>__<trial>/steps/milestone_N/verifier/reward.txt`.

Trial-level mean: `jobs/<job>/<task>__<trial>/result.json` under `stats.evals.oracle__adhoc.metrics[0].mean` (or `nop__adhoc`).

## Naming

- Task directories: lowercase-kebab-case (`go-context-propagation-mesh`).
- Zip filename matches the directory name (`go-context-propagation-mesh.zip`).
- **No canary strings** in any file — `CANARY-*`, `# canary GUID:`, and the `BENCHMARK DATA...` line are all retired in Edition 2.

## Rubrics live on the platform, not in files

Rubrics are authored **directly in the Snorkel submission UI** — never as a file in the task. A `rubric.md` / `rubric.txt` in the submission is ignored by the platform and is a rejection signal; the platform shows reviewers an empty rubric while the file sits unused.

- Emit **one `#Rubric N` block per milestone** (N = milestone number). Every criterion line **starts with `Agent`** and **ends with `, +N` / `, -N`** (e.g. `Agent identifies the root cause of the failing migration, +3`).
- Allowed scores: `±1, ±2, ±3, ±5`. **Never `4`.** (Tiers: critical ±5, major ±3, minor ±1–2.)
- At least **5 checks** per milestone, with **≥3 negative-reward** criteria.
- Positive scores **sum to 10–40** per milestone (the hard cap); **aim for ~10–20**.
- Criteria must be **trace-evidenced** and task-specific — confirmable from the agent's trace (surfaced output, counts, diff, exit code), naming exact paths/patterns; no "Agent understands the task" filler. Reward the act of verifying; don't restate the deterministic outcome. See [rubric.md](rubric.md) and [../00-core/anti-hallucination.md](../00-core/anti-hallucination.md).

## Schema version

This repo uses **Terminus Edition 2** task layout (`version = "2.0"`, `[metadata].number_of_milestones`, `[[steps]]` blocks). Harbor 0.8.0 accepts this directly — no migration to harbor-native `schema_version = "1.1"` / `[task]` shape needed.

## Files that do NOT belong in a task submission

These are common cleanup-issue rejections — none of them belong inside `tasks/<task-name>/` or the zip:

- `rubric.md` / `rubric.txt` (rubrics go in the platform UI — see above).
- `difficulty-check-summary.md` or any scratch/analysis notes.
- `.ruff_cache/`, `.pytest_cache/`, `__pycache__/`, `.mypy_cache/`.
- `.whl` files or a `wheels/` directory (test deps go in an isolated `/opt/verifier-venv`).
- AI-specific filenames (`CLAUDE.md`, `AGENTS.md`, `skills.md`) inside a task.

## Files that do NOT belong in the repo

- API keys, `.env` files with secrets.
- Local user paths in instructions or scripts.
- `node_modules/`, `target/`, `__pycache__/` (covered by `.gitignore`).
- Job output (`jobs/` is for local runs; gitignored).

## What goes into git vs. local-only

| Path | Tracked? |
|---|---|
| `rules/` | yes |
| `AGENTS.md`, `CLAUDE.md` | yes |
| `tasks/<task-name>/` (full tree) | yes |
| `tasksubmit/<task-name>.zip` | optional (the submission artifact; some teams track, some don't) |
| `jobs/` | **no** (gitignore) |
| `.cursor/rules/*.mdc` | yes (archived) |
| `ideas.md` | yes |
