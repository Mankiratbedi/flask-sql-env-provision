# 30-tests — `tests/test.sh`

**Scope:** Every `tests/test.sh` (flat task and each milestone's `tests/test.sh`).

`test.sh` is the verifier entry point. The harness invokes it; it must exit having written `/logs/verifier/reward.txt` with `0` or `1`. **The submission static checker enforces a literal reward tail** — `test.sh` must *end with* the exact block below.

## Canonical reward block (literal — static-check enforced)

The file must **end with** this block, byte-for-byte modulo the pytest line above it: bare `$?`, **4-space** indentation, ending at `fi`, with **nothing after** it.

```bash
if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
```

- The **pytest invocation is the last command immediately before** the `if`, so `$?` reflects pytest's exit code.
- Use **bare `$?`** inside the test — do **not** capture `RC=$?` into a variable.
- **Do not** add `exit "$RC"` (or any `exit`) after `fi`. The block is the end of the file.
- 4-space indentation on the two `echo` lines, exactly as shown.

> **The static checker rejects any other tail** with `❌ Must end with the reward section:` and prints the literal block above. Confirmed 2026-05-28: it rejected the `RC=$?` + `if [ "$RC" -eq 0 ]` + `exit "$RC"` form (the old default-template variant). That `RC=$?` form *runs* correctly under harbor, but it **fails the static gate**, so never ship it. Earlier revisions of this rule claimed "there is no literal-tail lint" — that was wrong and is retired.

## Working-directory guard

After creating `/logs/verifier` and **before** running pytest, guard against a
container launched with no working directory (`$PWD == "/"`). Write `0` to the
reward file and exit, so a misconfigured launch fails cleanly instead of running
tests from `/`:

```bash
if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile."
    echo 0 > /logs/verifier/reward.txt
    exit 1
fi
```

This is part of the recommended `test.sh` pattern (the accepted task
`capnp-segment-realigner` uses it). It writes the reward **before** exiting so the
harness never sees a missing `reward.txt`. It does not affect the literal reward
**tail** — that still ends the file (the guard is in the middle).

## Reference `test.sh` (flat task)

```bash
#!/bin/bash
set -uo pipefail

# Tests run from the isolated verifier venv (/opt/verifier-venv), built at image
# time. Runtime is offline; this script installs nothing and reaches no network.

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

For milestone tasks, the same pattern lives in each `steps/milestone_N/tests/test.sh`, scoped to that milestone's test file (`/tests/test_mN.py`). The `/opt/verifier-venv` is built once in the shared `environment/Dockerfile` (see [../20-environment/verifier-deps.md](../20-environment/verifier-deps.md)).

## Shell flags — `set -uo pipefail`

Use `set -uo pipefail` (treat unset variables as errors; propagate pipe failures). **Do not use `set -e`** as the script-wide flag: `set -e` exits on any non-zero status, and pytest exits non-zero on test failure — exactly the case we must handle by writing `0` to `reward.txt`. With `-e` off, a failing test does not abort the script before the reward block, so the bare `$?` in `if [ $? -eq 0 ]` correctly reads pytest's exit.

## Hard rules

- **Always** create `/logs/verifier/` before any other I/O.
- **Always** write `0` or `1` to `/logs/verifier/reward.txt`. Binary. No partial rewards.
- **Always** guard the working directory right after `mkdir -p /logs/verifier`: if `$PWD == "/"`, write `0` to the reward file and `exit 1` (see "Working-directory guard").
- **Always** make the pytest call the command **immediately before** the `if [ $? -eq 0 ]` block, so `$?` is pytest's exit. Nothing (not even a comment-only line is needed; a comment is harmless, but no *command*) may run between pytest and the `if`.
- **Always** end the file at `fi` — the literal block is the tail (no `exit`, no `RC=$?`).
- **Always** use the same logic for oracle and agent runs — no `if [ "$AGENT" = oracle ]` branching.
- **Never** exit before the reward block (don't let `set -e` or an early `exit` skip it).
- **Never** mask pytest's exit (`|| true`) — the reward would always be `1`.
- **Never** `pip install` or create a venv in `test.sh` — verifier deps are baked into the image (see [../20-environment/verifier-deps.md](../20-environment/verifier-deps.md)).

## Common bugs

| Symptom | Cause | Fix |
|---|---|---|
| `❌ Must end with the reward section` (static check) | Tail used `RC=$?`/`exit "$RC"`, wrong indent, or text after `fi` | End with the literal `if [ $? -eq 0 ]` block, 4-space indent, nothing after `fi` |
| `RewardFileNotFoundError` | `set -e` killed the script before the reward block | Use `set -uo pipefail`, not `set -e` |
| Reward is always `1` | `pytest` exit was masked (e.g., `\|\| true`) | Remove the mask |
| Reward is always `0` | `pytest` / plugin missing from the venv | Add the dep to the `/opt/verifier-venv` install |
| Reward ignores test result | another command ran between pytest and the `if`, clobbering `$?` | Put the `if [ $? -eq 0 ]` immediately after pytest |
| `pytest: not found` / `No module named pytest` | called system `python3` instead of the venv | Run `/opt/verifier-venv/bin/python -m pytest` |

## What `test.sh` is NOT for

- Computing answers (that's `solve.sh` for the oracle).
- Mutating `/app` (tests should be read-only over the agent's workspace, except `/logs/verifier/` writes).
- Recording or replaying terminal sessions.
- Calling `tmux` / `asciinema` directly (the harness uses them, not the verifier).

## Pre-zip verification

```bash
tail -6 tasks/<task-name>/tests/test.sh
# Confirm the file ENDS with:
#   if [ $? -eq 0 ]; then
#       echo 1 > /logs/verifier/reward.txt
#   else
#       echo 0 > /logs/verifier/reward.txt
#   fi
# pytest is the line immediately above the `if`; no `RC=`, no `exit` after `fi`.
```

For milestone tasks, repeat for every `steps/milestone_N/tests/test.sh`.
