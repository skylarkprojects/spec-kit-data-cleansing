---
description: "Validate that a previously resolved data issue is actually fixed and record the verification report"
---

# Verify Data Issue Resolution

Validate that the resolution recorded by `__SPECKIT_COMMAND_ISSUE_RESOLVE__` actually
fixes the issue described by `__SPECKIT_COMMAND_ISSUE_ASSESS__`. Output:
`instances/<name>/datasets/<dataset_id>/issues/<slug>/verify.md`.

## User Input

```text
$ARGUMENTS
```

Identify the issue: `slug=<issue-slug>`, a path containing the slug, or nothing (fall back
to context, same resolution order as `__SPECKIT_COMMAND_ISSUE_RESOLVE__`).

## Prerequisites

- `ISSUE_DIR/assessment.md` and `ISSUE_DIR/resolve.md` MUST both exist. If `resolve.md` is
  missing, stop and point to `__SPECKIT_COMMAND_ISSUE_RESOLVE__`.
- If `ISSUE_DIR/verify.md` already exists, ask before overwriting (interactive) or refuse
  (automated).

## Execution

1. **Plan the validation.**
   - Re-check the specific field/records named in `assessment.md` against the cleaned
     output.
   - Run `python scripts/validate_against_model.py validate-dataset` against the current
     cleaned output and target-data-model.md.
   - Run `python scripts/changelog.py verify <changelog.jsonl>` to confirm the resolution
     was actually logged and the chain is intact.

2. **Run the checks.** Capture command and result for each. If a check can't be run
   (e.g. no way to isolate the originally-affected records), record it as `not-run` with a
   reason rather than fabricating a result.

3. **Judge the outcome.**
   - **verified** — the symptom no longer reproduces and `validate-dataset` passes for the
     affected field(s).
   - **partial** — the named symptom is gone but a new violation appeared, or a check was
     inconclusive.
   - **failed** — the symptom still reproduces, or `validate-dataset` still fails for the
     affected field.

4. **Write the verification report** to `ISSUE_DIR/verify.md`:

   ```markdown
   # Data Issue Verification: <short title>

   - **Slug**: <ISSUE_SLUG>
   - **Dataset**: <dataset_id>
   - **Verified**: <ISO 8601 date>
   - **Assessment**: ./assessment.md
   - **Resolution**: ./resolve.md
   - **Result**: verified | partial | failed

   ## Summary

   <Does the issue reproduce, did the fix hold, any new violations.>

   ## Checks Performed

   | Check | Command | Result | Notes |
   |---|---|---|---|
   | Affected-field re-check | manual/query | pass/fail/skipped/not-run | <note> |
   | validate_against_model.py | `validate-dataset ...` | pass/fail | <note> |
   | changelog.py verify | `verify ...` | pass/fail | <note> |

   ## Residual Risks

   - <e.g. similar records elsewhere in the dataset not individually checked>

   ## Recommendation

   <"Close — verified." / "Hold — needs a broader re-check." / "Reopen — rerun
   __SPECKIT_COMMAND_ISSUE_ASSESS__ with new evidence.">
   ```

5. **Report back** with the slug, verify.md path, and result. If `failed`, recommend
   re-running `__SPECKIT_COMMAND_ISSUE_ASSESS__` with the new evidence.

## Guardrails

- This command MUST NOT modify the dataset or its artifacts — read and validate only.
- Never mark `verified` on `validate_against_model.py` output alone if the original
  assessment described a specific symptom you didn't actually re-check — downgrade to
  `partial`.
- Never overwrite an existing `verify.md` without confirmation.
