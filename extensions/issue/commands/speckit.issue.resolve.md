---
description: "Apply the remediation from a data issue assessment and log it to the dataset's changelog"
---

# Resolve Data Issue

Apply the remediation proposed by `__SPECKIT_COMMAND_ISSUE_ASSESS__` and record it in a
resolution report at `instances/<name>/datasets/<dataset_id>/issues/<slug>/resolve.md`.
Only valid after an assessment exists for the given slug.

## User Input

```text
$ARGUMENTS
```

Identify the issue to resolve: `slug=<issue-slug>`, a path containing the slug, or nothing
(fall back to context).

## Slug Resolution

1. Explicit user input.
2. Conversation context — reuse the slug `__SPECKIT_COMMAND_ISSUE_ASSESS__` just reported,
   confirmed by `issues/<slug>/assessment.md` existing.
3. Single candidate on disk under `issues/*/assessment.md`.
4. Otherwise: ask (interactive) or stop and list candidates (automated).

## Prerequisites

- `ISSUE_DIR/assessment.md` MUST exist — if not, stop and point to
  `__SPECKIT_COMMAND_ISSUE_ASSESS__`.
- If `ISSUE_DIR/resolve.md` already exists, ask before overwriting (interactive) or refuse
  (automated).
- Read `assessment.md` in full — its **Proposed Remediation** and **Artifacts likely to
  change** sections are the contract for this command.

## Execution

1. **Confirm the plan.** Restate in 3–6 bullets what you're about to change. If the
   verdict was `invalid`, stop — there's nothing to resolve.

2. **Apply the remediation, respecting the constitution and the stage gate:**
   - If the fix is a `plan.md` mapping/vocabulary correction: update `plan.md`, then
     re-run `python scripts/stage_gate.py check <entry.yaml> --stage tasks` — a plan
     change may require re-approving `plan` before `tasks.md` reflects it. Do not silently
     amend `tasks.md` to route around an unapproved plan change.
   - If the fix is a new or corrected cleaning operation: add it to `tasks.md` following
     the same checklist format as `04-tasks.md`, giving it the next `CL0XX` ID.
   - If the fix is a documented exception (raw data defect that cannot be corrected):
     record it per the constitution's escalation rule (flag vs. block) rather than forcing
     a transformation that fabricates a value.
   - Execute the new/corrected task against the dataset's working copy — never the raw
     source — and log it:
     ```
     python scripts/changelog.py append instances/<name>/datasets/<dataset_id>/changelog.jsonl \
         --dataset-id <dataset_id> --operation-id <CL0XX> \
         --description "<what was done>" --operator "<name>" \
         --task-source "issues/<slug>/assessment.md" \
         --input-ref "<ref>" --output-ref "<ref>" --reversible true \
         --notes "resolves issue <slug>"
     ```
   - If you discover the assessment's hypothesis was wrong, STOP, document the new finding
     under **Deviations from Assessment**, and recommend re-running
     `__SPECKIT_COMMAND_ISSUE_ASSESS__`.

3. **Write the resolution report** to `ISSUE_DIR/resolve.md`:

   ```markdown
   # Data Issue Resolution: <short title>

   - **Slug**: <ISSUE_SLUG>
   - **Dataset**: <dataset_id>
   - **Resolved**: <ISO 8601 date>
   - **Assessment**: ./assessment.md
   - **Status**: applied | partial | not-applied

   ## Summary

   <What was changed and why.>

   ## Changes

   | Artifact | Change | Notes |
   |---|---|---|
   | `plan.md` | amended mapping for field X | <note> |
   | `tasks.md` | added CL0XX | <note> |

   ## Changelog Entries

   - `CL0XX` — <description> (see changelog.jsonl)

   ## Deviations from Assessment

   <Empty if none.>

   ## Follow-ups

   - <e.g. amend target-data-model.md if the gap was in the target model itself>
   ```

4. **Report back** with the slug, the resolve.md path, status, and next step:
   `__SPECKIT_COMMAND_ISSUE_VERIFY__ slug=<ISSUE_SLUG>`.

## Guardrails

- Never touch the raw source file — only the working copy, per the constitution's raw
  immutability principle.
- Never edit `assessment.md` — record disagreements in `resolve.md` instead.
- Every applied change MUST be logged via `changelog.py` before this command reports
  `applied`.
- Never overwrite an existing `resolve.md` without confirmation.
