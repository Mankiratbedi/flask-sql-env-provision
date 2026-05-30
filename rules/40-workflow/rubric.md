# 40-workflow — Rubric authoring & chat output

**Scope:** The grading rubric for every task. Rubrics are **authored in the Snorkel platform UI**, never shipped as a file (a `rubric.md`/`rubric.txt` in the task is a rejection signal — see [repo-conventions.md](repo-conventions.md)). Because there is no rubric file in the submission, the assistant must **emit the rubric in the chat, ready to paste** into the platform.

## What a rubric is

A rubric is a set of **binary, objective checks over the agent's execution trace**. Each check awards points for a required, meaningful step that moves the task forward, or deducts points for an incorrect, unsafe, or wasteful step. It connects the task spec/assets, the deterministic tests, and the agent's trace — and is graded by an LLM judge that reads the trace check-by-check (YES → add the points, NO → add 0).

A rubric grades the **process**, not the outcome. The deterministic tests already verify the final state; the rubric verifies *how the agent got there*. **Do not mirror the outcome tests** — focus on the steps an agent must take to arrive at the correct answer, plus the edge cases and unsafe actions it must avoid.

## Block format: `#Rubric N` per milestone

- Emit **one block per milestone**, headed `#Rubric N` where **N is the milestone number** (`#Rubric 1`, `#Rubric 2`, `#Rubric 3`, …). For a flat task, emit a single `#Rubric 1` block.
- Every criterion line **starts with `Agent`** and **ends with `, +N` / `, -N`**.
- Each block stands alone for its milestone (don't reference other milestones' checks).

## When to emit

- Whenever you create or finalize a task (flat or milestone).
- Whenever the user asks for "the rubric."
- After any revision that changes what the agent must do — re-emit the affected milestone's block.
- After every (re)build of a task's `tasksubmit/` zip — re-emit the full set of blocks in the same turn.

The chat is the only delivery channel. Never write the rubric to a file in the task tree.

## How to author (before writing a single line)

1. Work out the **optimal/correct sequence of steps** that solves the task.
2. List **each key step in `solveN.sh`** (per milestone) that is necessary for success.
3. Give **every essential step ≥1 positive check**.
4. Add **edge-case and safety penalties** — the things that must *not* happen (destructive ops, scope violations, hardcoding, skipping verification).
5. Sanity-check the score shape: an **optimal** trace scores near the top, a **correct-but-sloppy** trace lower, an **incorrect or unsafe** trace low or negative.

## Trace-evidence is the hard test

**If you can't see it in the trace, you can't grade it.** Every criterion must be confirmable from the agent's trace alone. Phrase each check so it depends on visible evidence: surfaced command output, printed counts or paths, a diff, a checksum, an exit code, a re-run that prints zero findings.

- Bad (not trace-gradeable): `Agent parses the data correctly, +2`
- Good (trace-gradeable): `Agent runs the parser over /data/*.dat and prints all 6 records with coherent field values, +2`

Embed the expected evidence in the sentence (the command, the path, the value to look for) so the judge has something concrete to match.

## Importance tiers (choose a weight)

- **Critical (±5):** safety, core correctness, and the key steps without which success is unreliable.
- **Major (±3):** strongly recommended steps that materially affect reliability — verification, error recovery.
- **Minor (±1 to ±2):** good practice and hygiene — inspecting inputs before transforming, surfacing intermediate output, using the expected tool/flag.

`N ∈ {1, 2, 3, 5}`. **Never use a score of 4.**

## Output format (ready to paste)

Emit each milestone's criteria in a fenced block whose **first line is the `#Rubric N` header**, followed by the criterion lines and nothing else, so the user can copy a block straight into the platform UI. Print a one-line self-check immediately **after** each block (outside it).

```
#Rubric 1
Agent reads multiple documents under /app/docs/dossier/ before writing the spec, +2
Agent records coolant_flow_lpm with unit L/min, taking the email correction over the commissioning gal/min, +3
Agent excludes both ambient_humidity_pct and chamber_pressure_kpa from the model features, +3
Agent sets threshold.percentile to 97.5 (the postmortem revision) rather than the superseded 99.0, +3
Agent writes valid JSON to /app/artifacts/telemetry_spec.json following /app/docs/spec-format.md, +2
Agent uses the superseded 99.0 percentile for the threshold, -3
Agent keeps a deprecated channel as a model feature, -3
Agent writes the spec to a path other than /app/artifacts/telemetry_spec.json or as invalid JSON, -2
```
`#Rubric 1 — checks = 8 (≥5 ✓) · positives = 13 (10–20 ✓) · negatives = 3 (≥3 ✓) · no 4s ✓`

Emit `#Rubric 2`, `#Rubric 3`, … the same way, one block per milestone. Budgets apply **per milestone**.

## Line format (hard rules)

Each criterion line:

- **Starts with `Agent`** and names a single observable, trace-evidenced behavior.
- **Ends with `, +N` or `, -N`**, where N ∈ {1, 2, 3, 5}. **Never 4.**
- Is a single line, precise and behavior-focused.
- May credit the agent **running tests or verification and surfacing the result** (output, counts, diff, exit code) in the trace, e.g. `Agent executes the task tests and prints a pass/fail summary, +3`.
- Does **not** merely restate the deterministic outcome (`Agent's solution passes`, `all tests green`) — reward the *act* of verifying, evidenced in the trace.
- Does **not** name authoring machinery as the subject: `instruction.md`, `task.toml`, oracle, NOP, or metadata.

## Coverage & budget (per milestone)

- **≥ 5 checks** total.
- **≥ 3 negative-reward** criteria.
- **Positive scores sum to 10–40** (the hard platform cap); **aim for ~10–20**.
- **Every essential step** has at least one positive check.
- **One behavior → one check.** No double-counting.

## Content rules (anti-hallucination & specificity)

- Read the instruction, `solveN.sh`, and tests first; **every criterion must trace to a real behavior** the task requires or forbids.
- **Be specific.** Name the exact path, file, format, pattern, value, or command — not "the input file" or "the algorithm." Vague checks (`Agent reads input file`, `Agent implements core algorithm correctly`) are filler.
- No filler — never "Agent understands the task" / "Agent writes clean code".
- Positives reward meaningful engineering: root-cause identification, correct computation, edge-case/malformed-input handling, state/DB correctness, idempotency, inspecting before transforming, recovering from a surfaced error and re-running successfully.
- Negatives penalize destructive ops, scope violations (writing outside `/app`), leaking secrets, hardcoding outputs, deleting/weakening checks, bypassing real logic, ignoring malformed input, and claiming success while the trace shows failures.
- See [../00-core/anti-hallucination.md](../00-core/anti-hallucination.md).

## Don't

- Don't put the rubric in a committed file (`rubric.md`/`rubric.txt`).
- Don't use a score of 4.
- Don't write a criterion you can't confirm from the trace.
- Don't mirror the deterministic outcome tests — grade the process.
- Don't emit fewer than 5 checks or fewer than 3 negatives, or positives outside 10–40 — fix the criteria, never pad with filler.
- Don't name oracle/NOP/metadata/`instruction.md`/`task.toml` inside a criterion.
