# 90-reference — Accepted Patterns (examples)

**Scope:** Concrete examples — not rules. Use to ground new tasks in patterns that have shipped.

The canonical lane catalog is [../00-core/accepted-lanes.md](../00-core/accepted-lanes.md). This file lists *examples* of those lanes in this repo. **Inspect the actual task before assuming any of these is "accepted"** — the [accepted-patterns.md](accepted-patterns.md) file is a reference, not a stamp of approval.

## Existing tasks in this repo (lane-by-lane)

> Inspect the live task at `tasks/<name>/` before treating it as a template — these are working trees, not curated exemplars. Read the actual `task.toml`, `instruction.md`, and `tests/` before borrowing the pattern.

### Lane 2 — Go CLI / service debugging
- [`tasks/go-context-propagation-mesh`](../../tasks/go-context-propagation-mesh)

### Lane 3 — Rust parser / binary decoder
- [`tasks/rust-rocksdb-vv-merge`](../../tasks/rust-rocksdb-vv-merge)
- [`tasks/zig-lmdb-event-store`](../../tasks/zig-lmdb-event-store) — Zig variant of the binary-store pattern

### Lane 4 — Java service / config / migration
- [`tasks/virtual-thread-pinning-fix`](../../tasks/virtual-thread-pinning-fix)

### Lane 5 — Tool-specific local pipeline
- [`tasks/ffmpeg-avio-aes-gcm-verify`](../../tasks/ffmpeg-avio-aes-gcm-verify) — FFmpeg + AES-GCM verification
- [`tasks/imagemagick-magickwand-tilemap-c`](../../tasks/imagemagick-magickwand-tilemap-c) — ImageMagick + C
- [`tasks/perl-bastion-provisioner`](../../tasks/perl-bastion-provisioner) — Perl provisioning pipeline

### Lane 6 — DB interaction
- [`tasks/ruby-heist-sqlite-game`](../../tasks/ruby-heist-sqlite-game) — Ruby + SQLite
- [`tasks/lsm-tree-compaction-debug`](../../tasks/lsm-tree-compaction-debug) — LSM-tree storage internals

### Lane 7 — Milestone debugging (★ preferred)
- [`tasks/wandb-offline-provisioner`](../../tasks/wandb-offline-provisioner) — milestone task; harbor 0.8.0+ required
- [`tasks/lsm-tree-compaction-debug`](../../tasks/lsm-tree-compaction-debug) — if structured as milestones (verify)

### Other lanes seen here
- [`tasks/elixir-plug-webhook-vault`](../../tasks/elixir-plug-webhook-vault) — Elixir / Plug HTTP
- [`tasks/kotlin-marex-orderbook-rulebook`](../../tasks/kotlin-marex-orderbook-rulebook) — Kotlin financial rule engine
- [`tasks/marshal-vault-recovery`](../../tasks/marshal-vault-recovery) — serialization / recovery
- [`tasks/pcap-flow-aggregator`](../../tasks/pcap-flow-aggregator) — packet capture aggregation
- [`tasks/ripper-fee-dsl`](../../tasks/ripper-fee-dsl) — Ruby DSL

## Lane → task.toml template

### Lane 1 — TypeScript / Node API + SQLite

```toml
[metadata]
category = "software-engineering"  # or "debugging"
subcategories = ["api_integration", "db_interaction"]
difficulty = "hard"
codebase_size = "small"
languages = ["typescript"]
```

### Lane 2 — Go log replay / checksum repair

```toml
[metadata]
category = "debugging"
subcategories = []                  # or ["tool_specific"] if a real tool is central
difficulty = "hard"
codebase_size = "small"
languages = ["go"]
```

### Lane 3 — Rust binary decoder

```toml
[metadata]
category = "debugging"
subcategories = []
difficulty = "hard"
codebase_size = "small"
languages = ["rust"]
```

### Lane 4 — Java config migration

```toml
[metadata]
category = "software-engineering"
subcategories = ["db_interaction"]
difficulty = "medium"               # or "hard"
codebase_size = "small"
languages = ["java"]
```

### Lane 5 — Tool-specific pipeline

```toml
[metadata]
category = "data-processing"        # or "build-and-dependency-management"
subcategories = ["tool_specific"]
difficulty = "medium"               # or "hard"
codebase_size = "small"
languages = ["bash", "<tool's native lang>"]
```

### Lane 6 — DB interaction (SQLite)

```toml
[metadata]
category = "software-engineering"   # or "data-processing"
subcategories = ["db_interaction"]
difficulty = "hard"
codebase_size = "small"
languages = ["<primary>"]
```

### Lane 7 — Milestone debugging (★)

```toml
[metadata]
category = "debugging"              # or "software-engineering"
subcategories = ["db_interaction"]  # adjust to task
difficulty = "hard"
codebase_size = "small"
number_of_milestones = 3
languages = ["go"]                  # any non-Python primary

# NO root [agent] or [verifier] block — use [[steps]] instead

[[steps]]
name = "milestone_1"
[steps.agent]
timeout_sec = 1800.0
[steps.verifier]
timeout_sec = 300.0

[[steps]]
name = "milestone_2"
# ...
```

## Difficulty-source examples

**Good difficulty in the wild:**

- Multiple interacting bugs across 3+ files (`lsm-tree-compaction-debug`).
- DB constraints + rollback + idempotency together (lane 1 / 6).
- Byte-offset parsing under malformed input (`rust-rocksdb-vv-merge`).
- Cross-file schema mismatch (lane 1 / 4).
- Mutated fixtures so hardcoded outputs fail.

**Bad difficulty in the wild (rejected):**

- "Find the bug in this 50-line script."
- "Convert this CSV to JSON."
- "Read these three files and print a number."
- "Wrap your terminal session in tmux."

## When to reference this file

- Picking a category / subcategory combo.
- Sanity-checking that a task idea fits a known lane.
- Looking at a concrete example before scaffolding a new task.

When **not** to reference this file:

- Confirming whether a specific task in this repo "passed CI" — it may not have. Check `jobs/` for the actual run results.
- Treating a present task as canonically correct — every task in `tasks/` is a working tree, possibly mid-revision.
