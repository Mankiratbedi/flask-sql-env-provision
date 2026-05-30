# 00-core — Accepted Task Lanes

**Scope:** Applies to every new task idea and every new submission in this repo.

These are the lanes that survive review. Build inside them; do not bargain.

## Repo-wide defaults (this repo, all new tasks)

1. **Milestone-first.** Prefer multi-step milestone tasks (`steps/milestone_N/` layout) over flat tasks. Milestone tasks survive review more often because they expose multi-stage reasoning and give partial-credit signal. Build flat tasks only when the problem genuinely does not decompose.
2. **Non-Python primary language.** Go, TypeScript / Node, Rust, Java, Bash, Ruby, Zig, Elixir, Perl, Kotlin, C / C++ — pick whichever fits the problem. **Use Python only if the task is genuinely hard** (e.g., complex parsing, ML internals, autograd). Python "fix this script" tasks are rejected.
3. **No tmux as task subject.** `tmux` (and `asciinema`) **must be installed in the Docker image** — the harness requires them. But never design a task whose challenge is *about* tmux: don't ask the agent to wrangle tmux panes, sessions, scripted captures, or pipe replays. Same goes for asciinema.
4. **Difficulty:** `medium` or `hard` only. No `easy`, no `minimal`-codebase submissions.
5. **`codebase_size`:** `small` (20–199 env files) or `large` (≥200 env files). Never `minimal`. See [task-toml.md](../10-task-shape/task-toml.md).
6. **Single-container.** No multi-container compose unless explicitly approved.
7. **No internet at runtime.** `allow_internet = false`, always.

## Most accepted lanes

### 1. TypeScript / Node API + SQLite
- Category: `software-engineering` or `debugging`
- Subcategories: `api_integration`, `db_interaction`
- Strong behaviors: request validation, pagination, idempotency, transaction rollback, duplicate handling, report generation, malformed-input recovery.

### 2. Go CLI or service debugging
- Category: `debugging` or `data-processing`
- Strong behaviors: log replay, checksum repair, binary/JSONL decoding, restart handling, malformed record recovery, deterministic export.

### 3. Rust parser or binary decoder
- Category: `debugging`
- Strong behaviors: byte offsets, checksum validation, streaming decode, strict CLI output, deterministic artifact generation.

### 4. Java service / config / migration
- Category: `software-engineering`
- Subcategories: `api_integration` or `db_interaction`
- Strong behaviors: config precedence, schema migration, validation, retry policy, audit export.

### 5. Tool-specific pipeline (FFmpeg, ImageMagick, Graphviz, jq, SQLite, CMake, Cargo, npm)
- Category: `build-and-dependency-management` or `data-processing`
- Subcategories: `tool_specific`
- Strong behaviors: repair a pipeline, validate generated artifacts semantically, deterministic output.

### 6. DB interaction (SQLite preferred for single-container)
- Category: `software-engineering` or `data-processing`
- Subcategories: `db_interaction`
- Strong behaviors: migrations, constraints, indexes, backfill, rollback, query correctness.

### 7. Milestone debugging (★ preferred lane)
- Category: `debugging` or `software-engineering`
- 2–4 milestones; each milestone is a prerequisite for the next.
- Typical flow: M1 ingestion/parsing → M2 state/DB consistency → M3 reporting/export.

### 8. Long-context (rare; requires 50k+ token document with real semantic load)
- Subcategory: `long_context`
- Avoid documents solvable by grep or simple lookup.

## Avoid list (rejected on sight)

- Simple Python script repair / Python medium task.
- One failing unit test with one obvious bug.
- Pure CSV conversion / basic JSON formatting.
- "Read files and calculate" with no code repair.
- **Anything where the task subject is `tmux` / `asciinema` / terminal multiplexing / shell-replay capture.**
- UI-building tasks (unless explicitly approved).
- Multi-container compose tasks (unless explicitly approved).
- FastAPI-only tasks (unless unusually strong).
- Tasks where tests reveal the exact expected output.
- Tasks where the oracle just writes hardcoded output files.
- Tasks whose difficulty comes only from many edge cases enumerated in the instruction.
- Tasks with long checklist-like prompts.
- Tasks requiring internet data or external APIs.
- Latency / performance optimization tasks with timing thresholds.
- TerminalBench reskins (existing patterns with only names changed).
- Any task a frontier model can plausibly solve in one short edit.

## Good vs. bad difficulty

**Good difficulty:** multiple interacting bugs; persistent state across runs; DB constraints and rollback; malformed-input recovery; duplicate/replayed events; cross-file schema mismatch; deterministic computed reports; anti-cheat via mutated fixtures.

**Bad difficulty:** vague instruction; many random edge cases; brittle formatting; performance timing; secret exact strings not in instruction; tests that enforce unstated behavior; requiring a specific implementation rather than behavior.

## Difficulty threshold rule (when agent data exists)

Evaluate in order — stop at first match:

- **Hard:** best model ≤ 20%, **or** best > 20% AND worst ≤ 20%.
- **Medium:** worst > 20% and ≤ 60%.
- **Easy:** worst > 60% and ≤ 80% (not eligible for new submissions in this repo).

Without agent data, use **target difficulty** only.

## Default starter (when no specific idea is given)

A **milestone** task in one of lanes 1–6 above, leaning toward Go log-replay (lane 2), Rust binary decoder (lane 3), or TypeScript+SQLite reconciliation (lane 1). Default to medium-or-hard, small codebase, single container.
