# 20-environment — Dockerfile

**Scope:** `environment/Dockerfile` for every task. Deep reference for image best practices is in [../90-reference/canonical-spec.md](../90-reference/canonical-spec.md) (archived `terminus-dockerfile.mdc`).

## Required properties

Every image must be: **reproducible** (same source → same image), **cacheable** (shared layers), **auditable** (digest-pinned, no secrets), **complete** (no network at runtime), **siloed** (no leaked tests/solution), and **resourced** (limits set in `task.toml`).

## Hard rules

### 1. `tmux` and `asciinema` are mandatory

The harness requires both. Missing either causes agent runs to fail with no verifier output.

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        asciinema \
        ca-certificates \
        tmux \
        <other apt deps> \
    && rm -rf /var/lib/apt/lists/*
```

This is the **only** reason `tmux` exists in the image. **Never design a task whose subject is tmux/asciinema** — see [../00-core/accepted-lanes.md](../00-core/accepted-lanes.md).

### 2. Pin base images by digest

```dockerfile
# Bad
FROM python:3.13-slim-bookworm

# Good
FROM python:3.13-slim-bookworm@sha256:<digest>
```

Never `latest`. Tags allowed for readability, but the digest is the source of truth.

### 3. Pin every app dependency exactly

| Ecosystem | Lock file |
|---|---|
| Python | `requirements.txt` (exact versions), `uv.lock`, `poetry.lock` |
| Node | `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock` |
| Rust | `Cargo.lock` |
| Go | `go.mod` and `go.sum` |
| JVM | Maven/Gradle locks |

Pin downloaded binaries by version and checksum — never `curl | sh` without `sha256sum -c`.

### 4. Build verifier deps into an isolated venv (not the system Python)

Install `pytest`, `pytest-json-ctrf`, and any other **test-only** deps into a dedicated
venv at `/opt/verifier-venv` at build time — **not** into the image's system/app Python.
Test-only deps in the system environment **fail** the `test_deps_in_image` check. The
venv keeps them isolated to the test runner while staying offline-capable at runtime.
See [verifier-deps.md](verifier-deps.md).

```dockerfile
# apt layer must include python3-venv
RUN python3 -m venv /opt/verifier-venv \
 && /opt/verifier-venv/bin/pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5
```

`test.sh` then runs `/opt/verifier-venv/bin/python -m pytest …`. Do **not** ship `.whl`
files or a `wheels/` directory under `tests/`, and do **not** install test deps into the
base interpreter (`pip install --break-system-packages`).

### 5. Never copy `solution/` or `tests/` into the image

```dockerfile
# Forbidden
COPY solution /app/solution
COPY tests /app/tests
COPY . /app                    # blanket COPY pulls in tests/ and solution/
```

The verifier mounts them at runtime. The image must not contain them.

### 6. Layer order — least volatile to most volatile

```dockerfile
FROM <base>@sha256:...

# 1. OS / system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ... && rm -rf /var/lib/apt/lists/*

# 2. Runtime / package manager
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 3. App manifests
COPY package.json package-lock.json /app/

# 4. App dependencies
RUN cd /app && npm ci --offline

# 5. App source (most volatile)
COPY src/ /app/src/

WORKDIR /app
```

Task edits should invalidate only the top layers.

### 7. `.dockerignore` is required

`environment/.dockerignore` keeps tests/solution out of the build context:

```
.git
.gitignore
**/__pycache__/
**/*.pyc
**/.pytest_cache/
**/.mypy_cache/
**/.ruff_cache/
**/node_modules/
**/target/
**/dist/
**/build/
**/.venv/
**/venv/
.env
*.log
solution/
tests/
```

### 8. Narrow `COPY`

Prefer `COPY src/ /app/src/` over `COPY . /app`. Use `--chmod=0755` and `--chown=user:user` to set permissions at copy time.

### 9. No build steps with wall-clock / random side effects

Don't embed timestamps, random paths, or usernames. Set `SOURCE_DATE_EPOCH` where applicable.

### 10. No fetching task data at runtime

All app fixtures live in the image (or are mounted from `environment/`). Oracle must pass with `allow_internet = false`.

### 11. Resources declared in `task.toml`

See [../10-task-shape/task-toml.md](../10-task-shape/task-toml.md). Oracle must pass within `[environment]` limits.

## Image hygiene blockers

Don't include in the image:

- `.git`, `.env`, credentials, SSH keys.
- Package-manager / compiler caches (`~/.cargo/registry`, `~/.npm`, `__pycache__/`).
- Unused build tools.
- Hidden solution files or expected outputs.
- AI-specific filenames (`CLAUDE.md`, `skills.md`).

Clean up in the same layer:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
```

## Audit checklist (Dockerfile)

- [ ] Every `FROM` uses `@sha256:` digest.
- [ ] `tmux` and `asciinema` present.
- [ ] App deps pinned + lockfile committed.
- [ ] Verifier deps (pytest / pytest-json-ctrf) **installed and pinned** in the image.
- [ ] **No** `.whl` files or `wheels/` dir under `tests/`.
- [ ] `solution/` and `tests/` **not** copied.
- [ ] `.dockerignore` present and excludes `tests/`, `solution/`.
- [ ] No `latest` tags anywhere.
- [ ] Layer order goes least → most volatile.
- [ ] No secrets / hidden hints / ground-truth files copied.
