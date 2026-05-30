# 20-environment — Runtime Verifier (offline)

**Scope:** `[environment]` block in `task.toml` and the network-discipline of `tests/test.sh`.

The verifier and the agent both run with `allow_internet = false`. Anything that would touch the network at runtime is a blocker.

## `task.toml` requirement

```toml
[environment]
allow_internet = false       # ALWAYS
build_timeout_sec = 600.0
cpus = 2
memory_mb = 4096
storage_mb = 10240
```

**Do not set `workdir` on flat (non-milestone) tasks** — per 2026-05-27 trial feedback it is a milestone-only field. See [../10-task-shape/task-toml.md](../10-task-shape/task-toml.md).

## What `test.sh` may NOT do

These are blockers if they appear in `tests/test.sh` (any milestone):

- `curl`, `wget` (anywhere except `command -v` style probes).
- `apt-get install`, `apt install`.
- `pip install` **without** `--no-index` (every `pip install` must be offline).
- `uv install`, `uvx <pkg>` that resolves from PyPI.
- `npm install` from registry (offline npm with `--offline` is fine).
- `npx playwright install` (download flavor).
- `cargo fetch`, `mvn dependency:get`, `go mod download` against the network.
- Any other runtime download.

## What `test.sh` may do

- Create `/logs/verifier/`.
- Copy tests to `/tmp/` or use `TEST_DIR="${TEST_DIR:-/tests}"`.
- Write `/logs/verifier/ctrf.json`.
- Run `/opt/verifier-venv/bin/python -m pytest` (the isolated verifier venv, built at image time).
- Write `0` or `1` to `/logs/verifier/reward.txt` (binary, no partial credit).

It must **not** `pip install` or create a venv at runtime — the verifier venv is built into the image at build time.

## Where verifier deps live

Test-only packages (pytest, pytest-json-ctrf, numpy, …) are built into an **isolated venv at `/opt/verifier-venv`** at image-build time — **not** the system/app Python (that fails the `test_deps_in_image` check). `tests/` holds only test scripts — no `wheels/`, no `.whl`. See [verifier-deps.md](verifier-deps.md).

## App-runtime deps are different

Anything the agent's code imports / executes at runtime (the Python/Node/Rust libs, system packages, the language toolchain itself) belongs in `environment/Dockerfile`, pinned. The "no verifier deps in image" rule does **not** apply to app deps.

## Comments

Do **not** add a verifier-deps comment to `task.toml` — reviewers have cited a
"verifier deps are installed in environment/Dockerfile" line as corroborating evidence
of a `test_deps_in_image` violation. A short `tests/test.sh` header is fine:

```bash
# Runs the tests from the isolated verifier venv (/opt/verifier-venv). Runtime is
# offline; this script installs nothing and reaches no network.
```

Never cite internal rule filenames in committed task files.

## Deprecated patterns (treat as blockers when seen)

- **Deprecated #1:** any `pip install` inside `tests/test.sh` (runtime is offline — build the venv at image time instead).
- **Deprecated #2:** `.whl` files or a `wheels/` directory under `tests/` (or `steps/*/tests/`).
- **Deprecated #3:** a venv (`/opt/verifier-venv`, `/tmp/verifier-venv`, …) created at *runtime* inside `test.sh` — build it at *image* time.
- **Deprecated #4:** test-only deps installed into the image's **system** Python (incl. `pip install --break-system-packages`) — they must go in the isolated venv.

All replaced by **a `/opt/verifier-venv` built at image time** + `test.sh` running `/opt/verifier-venv/bin/python -m pytest`.

## Pre-zip verification

Read the actual files and confirm:

1. `task.toml` has `[environment] allow_internet = false`, no `workdir` on flat tasks, and **no** verifier-deps comment.
2. `environment/Dockerfile` builds `/opt/verifier-venv` and installs test deps there (system Python stays clean); `python3-venv` is in the apt layer.
3. `tests/` has no `wheels/` dir and no `.whl` files.
4. `tests/test.sh` runs `/opt/verifier-venv/bin/python -m pytest` — no `pip install`, no venv creation, no network call.

Don't claim "verifier setup is okay" without checking all four.
