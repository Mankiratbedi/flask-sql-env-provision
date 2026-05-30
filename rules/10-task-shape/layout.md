# 10-task-shape — Directory Layout

**Scope:** Applies to every new task's on-disk structure.

## Non-milestone (flat) layout

```
tasks/<task-name>/
  instruction.md
  task.toml
  environment/
    Dockerfile
    .dockerignore
    <agent-visible files>
  solution/
    solve.sh
  tests/
    test.sh
    test_outputs.py
    verifier-tools/        # optional reference utilities
    # no wheels/ — test deps live in /opt/verifier-venv (built in environment/Dockerfile)
```

## Milestone layout (preferred per [accepted-lanes.md](../00-core/accepted-lanes.md))

```
tasks/<task-name>/
  task.toml
  environment/
    Dockerfile
    .dockerignore
    <agent-visible files>
  steps/
    milestone_1/
      instruction.md
      tests/
        test.sh
        test_m1.py
      solution/
        solve.sh
        solve1.sh
    milestone_2/
      instruction.md
      tests/
        test.sh
        test_m2.py
      solution/
        solve.sh
        solve2.sh
    ...
```

### Milestone hard rules

- **Never** create a root-level `instruction.md`, `tests/`, `solution/`, `milestones.md`, `milestone_1.md`, root `solveN.sh`, or root `test_mN.py` in a milestone task.
- Each milestone owns its own `instruction.md`, `tests/`, and `solution/`.
- Each milestone's `instruction.md` covers **only that milestone** — never reveal future milestones.
- Each milestone's `tests/test_mN.py` defines class `TestMilestoneN`.
- Each milestone's `solution/solve.sh` is a thin wrapper that calls `solveN.sh` (the actual oracle for that milestone).
- `solveN.sh` solves **only** its own milestone unless explicitly required to set up state for the next.
- Each milestone depends on the previous milestone's state but must not reveal it.

## What never goes inside `environment/`

- Tests (`test.sh`, `test_*.py`).
- Solution scripts (`solve*.sh`).
- Ground-truth files (`expected_*.json`, `answer.txt`).
- Hidden hints, `BUG:` comments, `TODO: solution here` markers.
- Hidden expected-output snapshots.
- AI-specific filenames (`CLAUDE.md`, `skills.md`, `AGENTS.md` — those belong at repo root if anywhere).

Anything under `environment/` is agent-visible. Treat it as the user-facing workspace.

## What never gets copied into the Docker image

- `solution/` (any form).
- `tests/` (any form).
- Hidden verifier-tools.

The verifier mounts `tests/` and `solution/` at runtime; the image must not contain them. See [../20-environment/dockerfile.md](../20-environment/dockerfile.md).

## Cross-check before zipping

```bash
ls -la tasks/<task-name>/
# Flat:   instruction.md, task.toml, environment/, solution/, tests/
# Milestone: task.toml, environment/, steps/milestone_1/.../, ...
```

If you see both a root `instruction.md` *and* a `steps/` directory, the layout is broken — pick one.
