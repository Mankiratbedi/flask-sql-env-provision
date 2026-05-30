# 30-tests — Oracle / NOP Contract

**Scope:** `solution/solve.sh` (or `solveN.sh`) and `tests/test_outputs.py` (or `test_mN.py`) together. The contract: **oracle reward = 1.0; nop reward = 0.0.** Anything else is a broken task.

## The contract

| Run | What runs | Required reward |
|---|---|---|
| **oracle** | `solve.sh` then `test.sh` | `1.0` (every milestone if multi-step) |
| **nop** | only `test.sh` (no solve) | `0.0` (every milestone if multi-step) |

`reward.txt` is binary: `1` or `0`. The trial-level mean (in `result.json` under `stats.evals.<run>.metrics[0].mean`) must be `1.000` for oracle and `0.000` for nop.

## Oracle (`solve.sh` / `solveN.sh`) must

- Be **deterministic.** Same inputs → same outputs every run.
- Be **self-contained.** No network, no machine-specific paths, no user-specific config.
- **Compute** the answer through real steps. Never `echo '{"result": 42}' > /app/output.json` — that's a hardcoded oracle and a rejection trigger.
- Be **idempotent** when possible (running twice produces the same state).
- Avoid randomness; if needed, seed it.
- Not depend on local machine state outside the task.
- Be executable (`chmod +x solve.sh`).

For milestones:

- `solveN.sh` solves **only** milestone N.
- `solve.sh` is a thin wrapper that calls `solveN.sh` (or sequences them if the harness needs cumulative state).
- Never pre-solve future milestones unless the contract explicitly requires it.

## NOP (no solution applied) must

- See an `/app` whose default state does not satisfy `test_outputs.py`.
- See tests that fail when the agent's output is missing, wrong, or default.
- Return `0` from `pytest`, causing `reward.txt = 0`.

## How tests enforce both sides

### Anti-cheat against hardcoded oracles

Tests should **mutate fixtures** so that hardcoded outputs become wrong:

```python
# Setup mutates the fixture so a hardcoded oracle answer fails
def setup_module(module):
    # Reshuffle the test orders so the "correct" report depends on this seed
    seed = int(os.environ.get("TB_VARIANT_SEED", "1729"))
    regenerate_fixture("/app/data/orders.jsonl", seed=seed)
```

Equally: compute the expected value **inside the test** from the (mutated) inputs, then compare to what the agent produced. Don't hardcode `assert output == 42` — compute `42` from the inputs.

### Anti-cheat against trivial NOP passes

Common ways tests accidentally pass under NOP:

1. **File-existence-only assertions.** `assert os.path.exists("/app/output.json")` passes if the agent (or no one) creates an empty file. Always pair existence with a schema and value check.
2. **Default-value tests.** If a config defaults to `"enabled": true` and the test expects `true`, NOP passes. Mutate the default or override it in the test setup.
3. **Pre-populated expected outputs in `environment/`.** If `expected_report.json` is in `/app`, a no-op run that reads-and-copies it passes. Never put expected outputs in agent-visible paths.
4. **Tests that read the same source the oracle writes.** If the test reads `/app/output.json` and the oracle writes `/app/output.json`, NOP fails because the file doesn't exist — good. But if the test reads `/app/data/source.csv` (which is in `environment/`) and computes the answer itself, NOP passes — bad. Tests must verify the **agent's output**, not recompute from inputs.

### Behavior validation, not file existence

Each test should answer: "Did the agent actually produce the right behavior?" not "Did a file appear?"

```python
# Weak — passes on a no-op that happens to leave an empty dict
def test_report_exists():
    assert os.path.exists("/app/output/report.json")

# Strong — fails when the agent didn't compute anything
def test_report_reconciles_imbalanced_batch():
    with open("/app/output/report.json") as f:
        report = json.load(f)
    # Expected value computed from mutated fixture, not hardcoded
    expected = compute_expected_reconciliation("/app/data/orders.jsonl")
    assert report["net_position"] == pytest.approx(expected["net_position"], rel=1e-6)
```

## Common reasons oracle fails

| Symptom | Cause | Fix |
|---|---|---|
| Oracle reward `0` despite working logic | Path mismatch between `solve.sh` and `test_outputs.py` | Grep all files for the path; fix the drift |
| Oracle reward `0` after first success | Non-determinism (unseeded RNG, timestamp embedded in output) | Seed RNG, freeze timestamps |
| Oracle reward `0` only on platform | Local `pip` cache hid a missing dep; image lacks it | Pin the dep in `Dockerfile`, rebuild |
| Oracle reward `0` for milestone N>1 | Milestone N-1's solve was not actually applied | Confirm `solve.sh` runs all `solveN.sh` cumulatively for the oracle run |

## Common reasons NOP passes (and shouldn't)

| Symptom | Cause | Fix |
|---|---|---|
| NOP reward `1` | Expected output file already in `environment/` | Remove it; tests must require the agent to produce it |
| NOP reward `1` | Test only asserts `os.path.exists` | Add behavior/value assertions |
| NOP reward `1` | Test reads from `environment/` source, recomputes answer, compares to itself | Test must read agent-produced artifact and compare to independently-computed expected value |
| NOP reward `1` | Default `/app` state happens to satisfy assertions | Mutate the default in the test setup, or assert on a value impossible to match without computation |

## Verification

Before zipping, run both:

```bash
harbor run -p tasks/<task-name> -a oracle --job-name "oracle__<task>__$(date +%Y%m%d-%H%M%S)" -q
harbor run -p tasks/<task-name> -a nop    --job-name "nop__<task>__$(date +%Y%m%d-%H%M%S)" -q
```

Then check the per-step reward files and the trial-mean. See [../00-core/quality-gates.md](../00-core/quality-gates.md) gates 3 and 4.
