# 10-task-shape — `instruction.md`

**Scope:** The single markdown file the agent sees as its prompt. Applies to flat-task `instruction.md` and to each `steps/milestone_N/instruction.md` independently.

Write it like a real user asking a coding agent for help — not like an AI prompt engineer.

## The six principles

1. **Concise.** One sentence to three short paragraphs (≈150–200 words). The challenge lives in the code, not in the prompt. Long checklists are a rejection signal.
2. **Well specified.** The goal is clear to a human reader. Edge-case enumerations don't belong inline — link to a contract doc under `/app/docs/` instead.
3. **Interesting.** A real developer would recognize the problem. No contrived, made-up scenarios.
4. **No answers, no hints.** Requirements yes; how-to-solve no. No stepwise guidance, no "look in this file", no exit-code lookup tables, no rubric-like enumerations.
5. **Unique.** Initial state, instruction, **or** expected output must be non-trivially different from any existing Terminal-Bench 2/3 or Project Terminus Edition 1 task. Similarity-search results decide.
6. **Absolute paths and no canary string.** Every file or directory mentioned uses an absolute path (`/app/...`). Never include the task name. Never include a `CANARY-*` marker or any canary string.

## Tone — human-centric vs. synthetic

| Axis | Synthetic (reject) | Human-centric (accept) |
|---|---|---|
| Tone | "You are an expert programmer. Your goal is to..." | "We need to migrate the existing SQLite schema to..." |
| Length | 500+ words of redundant context. | 150–200 words of actionable info. |
| Guidance | "First, use `ls` to see files, then..." | "The source data is in `/app/data`. Write the result to `/app/out/...`." |

**Bad:** "First inspect `/app/src/parser.ts`, then change the checksum function to..."

**Good:** "The import service under `/app` is producing inconsistent reconciliation reports for replayed order batches. Fix the service so it handles restarts, duplicate events, and malformed records correctly, then write the normalized report to `/app/output/reconciliation-report.json` using the schema described in `/app/docs/report-format.md`."

## Must include

- **Absolute paths** for every file or directory mentioned.
- **Required output files and schemas** — by linking to a doc under `/app/docs/`, not by inlining the spec.
- Mention of every behavior the tests verify (explicitly, clearly implied, or via the linked contract).
- A realistic developer framing.

## Must avoid

- Excessive markdown, long bullet lists, emojis, "expert programmer" framing, LLM-style phrasing.
- Stepwise solution guidance.
- "Look in this file for the bug" — unless file location is necessary user context.
- Exact algorithmic recipes (unless they are part of the product contract).
- The task name and canary strings.
- Tool requirements that cannot be verified ("use vim").
- Inline enumerations of exit codes, mode bits, JSON keys — point to the contract doc.
- Edge-case checklists as the only source of difficulty.

## Milestone-specific

- Each milestone's `instruction.md` is a standalone prompt — written as if the next milestone does not exist.
- Reference earlier milestones' artifacts only through their committed paths (e.g., "the parsed events file at `/app/data/events.jsonl` produced earlier"), never by describing how they were produced.
- Never include "next, you will..." or otherwise reveal the milestone chain.

## Audit checklist (before declaring done)

- [ ] Word count between roughly 100 and 250.
- [ ] All paths absolute (`grep -E '(^|[^/])(\./|\.\./)' instruction.md` returns nothing).
- [ ] No task name, no `CANARY-*` string.
- [ ] Every test assertion maps to something stated or linked.
- [ ] Tone reads as a developer ticket, not an LLM prompt.
- [ ] Output paths match `test_outputs.py`, `Dockerfile`, and `solve.sh` byte-for-byte.
