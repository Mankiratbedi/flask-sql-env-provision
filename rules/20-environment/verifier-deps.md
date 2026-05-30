# 20-environment — Verifier Dependencies

**Scope:** Where verifier/test-only Python packages (pytest, pytest-json-ctrf, numpy, …) live for every task.

> **Policy (per 2026-05-28 `test_deps_in_image` review):** test-only deps must be **isolated to the test runner** — installed into a dedicated venv at **`/opt/verifier-venv`** built at image time — **not** into the image's system/app Python, and **not** vendored as `.whl` under `tests/`. Installing them into the base interpreter (e.g. `pip install --break-system-packages`) **fails** the `test_deps_in_image` check, even with an offline justification.

## What the checker wants

`test_deps_in_image` flags pytest/numpy/etc. that end up in the application image's
**system** environment. A venv satisfies it: the deps are still baked into the image
(so the offline runtime needs no network) but they are isolated from the app/system
Python — i.e. "isolated to the test runner." This is the pattern the accepted task
`capnp-segment-realigner` uses.

## Hard rules

- **Build a dedicated venv at image time:** `python3 -m venv /opt/verifier-venv` then
  `/opt/verifier-venv/bin/pip install …` the test deps, pinned. Requires `python3-venv`
  in the apt layer.
- **Never** install test-only deps into the system interpreter (`pip install`,
  `pip3 install --break-system-packages`, `apt-get install python3-pytest`).
- `tests/` contains only `test.sh`, `test_*.py`, and optional `verifier-tools/*.py`.
  **No `wheels/` directory. No `.whl` files. No `pip install` / `python -m venv` inside
  `test.sh`** (the venv is built at *image* time, not *test* time).
- `test.sh` runs pytest from the venv: `/opt/verifier-venv/bin/python -m pytest …`.
- The Docker **build** may reach the network; the **runtime** stays offline (`allow_internet = false`).
- **Do not** add a verifier-deps comment to `task.toml` (a "deps installed in the
  Dockerfile" line has been cited by reviewers as evidence of the violation).

## Dockerfile (reference)

```dockerfile
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      asciinema ca-certificates python3 python3-venv tmux \
 && rm -rf /var/lib/apt/lists/*

# Test-only deps in an isolated venv (the test runner), kept out of the app/system Python.
RUN python3 -m venv /opt/verifier-venv \
 && /opt/verifier-venv/bin/pip install --no-cache-dir \
      pytest==8.4.1 \
      pytest-json-ctrf==0.3.5
```

If the verifier needs extra test-only deps (`numpy`, `hypothesis`, …), add them to the
same venv install. To also clear the lockfile ⚠️ warning, install a hash-pinned
`requirements.lock` *into the venv* (`COPY requirements.lock /tmp/` then
`/opt/verifier-venv/bin/pip install --require-hashes --no-deps -r /tmp/requirements.lock`);
generate it with `uv pip compile requirements.in --generate-hashes --python-version <img-py>`.

## `test.sh` (reference)

```bash
#!/bin/bash
# Runs the tests from the isolated verifier venv; runtime is offline.
set -uo pipefail
mkdir -p /logs/verifier

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile."
    echo 0 > /logs/verifier/reward.txt
    exit 1
fi
/opt/verifier-venv/bin/python -m pytest -o cache_dir=/tmp/pytest_cache \
  --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
```

The file must **end** with that `if [ $? -eq 0 ]` block (bare `$?`, ends at `fi`, no
`RC=$?`/`exit`); the static checker rejects the `RC=$?`/`exit "$RC"` variant. See
[../30-tests/test-sh.md](../30-tests/test-sh.md).

## App-runtime deps are different

Anything the agent's app imports/executes at runtime (the Node/Python/Rust libs, the
language toolchain) belongs in the **normal** image build (e.g. `npm ci` from a committed
lockfile, `cargo build`). Only **test-only** deps need the venv isolation.

## Deprecated patterns (blockers when seen)

- Test-only deps installed into the image's **system** Python (incl. `--break-system-packages`).
- A `wheels/` directory or any `.whl` under `tests/` (or `steps/*/tests/`).
- `pip install` or `python -m venv` **inside `test.sh`** (build the venv at image time).
- A verifier-deps comment in `task.toml`.

## Audit checklist

- [ ] `environment/Dockerfile` builds `/opt/verifier-venv` and installs test deps there, pinned.
- [ ] System Python has **no** pytest/numpy (`docker run … python3 -c "import pytest"` fails).
- [ ] `python3-venv` is in the apt install.
- [ ] No `wheels/` dir and no `.whl` files anywhere under `tests/`.
- [ ] `test.sh` runs `/opt/verifier-venv/bin/python -m pytest` — no `pip install`, no venv creation.
- [ ] No verifier-deps comment in `task.toml`.
- [ ] `allow_internet = false` and no runtime network call.
