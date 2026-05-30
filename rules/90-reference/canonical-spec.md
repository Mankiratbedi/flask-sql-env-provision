# 90-reference — Canonical Spec (archive)

**Scope:** Pointer to the legacy `.cursor/rules/*.mdc` files. **Do not load by default.** Consult only when something in `rules/00-core` through `rules/40-workflow` is silent on a question.

The current rules in `rules/` supersede the archive. If the archive disagrees with `rules/`, **the new files win**.

## Archive locations

The Cursor-IDE `.mdc` files remain in place for editor compatibility and as a deep reference:

| File | Lines | What it covers |
|---|---|---|
| [`.cursor/rules/terminus.mdc`](../../.cursor/rules/terminus.mdc) | 1086 | Full canonical spec — the deep dive. **Last-resort reference only.** |
| [`.cursor/rules/terminus-core.mdc`](../../.cursor/rules/terminus-core.mdc) | 70 | Original anti-hallucination + pre-submit checklist → now in [../00-core/](../00-core/) |
| [`.cursor/rules/terminus-accepted-patterns.mdc`](../../.cursor/rules/terminus-accepted-patterns.mdc) | 149 | Lanes + avoid list + difficulty thresholds → now in [../00-core/accepted-lanes.md](../00-core/accepted-lanes.md) |
| [`.cursor/rules/terminus-creation-rules.mdc`](../../.cursor/rules/terminus-creation-rules.mdc) | 258 | Layout, instruction, tests, oracle, rubric → split across [../10-task-shape/](../10-task-shape/) and [../30-tests/](../30-tests/) |
| [`.cursor/rules/terminus-dockerfile.mdc`](../../.cursor/rules/terminus-dockerfile.mdc) | 338 | Extended Snorkel Dockerfile spec (15 sections) → summary in [../20-environment/dockerfile.md](../20-environment/dockerfile.md) |
| [`.cursor/rules/terminus-runtime-verifier.mdc`](../../.cursor/rules/terminus-runtime-verifier.mdc) | 140 | Offline verifier rules → now in [../20-environment/runtime-verifier.md](../20-environment/runtime-verifier.md) and [../20-environment/verifier-deps.md](../20-environment/verifier-deps.md). **NB:** the archive's vendored-wheels guidance is superseded — Edition 2 installs verifier deps in the Dockerfile. |
| [`.cursor/rules/terminus-workflows.mdc`](../../.cursor/rules/terminus-workflows.mdc) | 101 | Audit / revision / final verify → now in [../40-workflow/](../40-workflow/) |
| [`.cursor/rules/terminus-repo-workflow.mdc`](../../.cursor/rules/terminus-repo-workflow.mdc) | 39 | This-repo conventions → now in [../40-workflow/repo-conventions.md](../40-workflow/repo-conventions.md) |
| [`.cursor/rules/terminus-index.mdc`](../../.cursor/rules/terminus-index.mdc) | 21 | Old index → superseded by [../index.md](../index.md) |

Total archive ≈ 2,200 lines. The current `rules/` tree distills these into ~17 focused files.

## When to read the archive

- A question is genuinely uncovered by `rules/00-core` through `rules/40-workflow`.
- You're investigating a corner case (rubric scoring fine print, exotic ecosystem, multi-stage Docker build, multi-container approval flow).
- You want the original Snorkel image-best-practices wording.

## When NOT to read the archive

- During normal task creation / revision / packaging — the current `rules/` files are complete for those workflows.
- When you would rather skim a long file than read the focused split.
- To resolve a conflict between the new files and the archive — the **new files win**. Don't drag the archive into the resolution.

## Drift policy

The `.cursor/rules/*.mdc` files are a **maintained mirror** of `rules/`, not a frozen archive. `rules/` stays canonical — on any conflict, the `rules/` files win. If a rule changes:

1. Update the relevant file under `rules/`.
2. Update [../index.md](../index.md) if structure changed.
3. If the change is a recurring override or correction, also add it to the memory layer.
4. Mirror the change into the matching `.cursor/rules/*.mdc` file(s) so the two stay in sync.

(The `.cursor` files were treated as a frozen archive previously; that changed on 2026-05-28 when the `.cursor` mirror was brought back in sync with the Edition-2 trial-feedback rule changes.)
