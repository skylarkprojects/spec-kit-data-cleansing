---
description: Execute only what's in the approved tasks.md, logging every operation. Refuses to run against a dataset whose tasks.md isn't approved.
---

## User Input

The instance name and `dataset_id` for a dataset whose tasks stage is approved.

## Precondition

```
python scripts/stage_gate.py check instances/<name>/registry/<dataset_id>.yaml --stage implement
```

If this reports `BLOCKED`, **stop** — do not execute any cleaning operation against this
dataset. This is a hard refusal, not a warning: an unapproved `tasks.md` may encode a
scope or mapping decision no one has reviewed.

## Steps

1. **Load** `instances/<name>/datasets/<dataset_id>/tasks.md`,
   `instances/<name>/datasets/<dataset_id>/plan.md`, and
   `instances/<name>/constitution.md` (for the reversibility/logging requirements).

2. **Execute phase by phase**, respecting task order and `[P]` parallelism, working from a
   copy of the raw source — never the raw file itself (Principle I). For each task:
   - Perform exactly the operation the task describes — nothing broader.
   - Run the task's own validation check; if it fails, stop and report rather than
     continuing past a failed validation.
   - Log it immediately:
     ```
     python scripts/changelog.py append instances/<name>/datasets/<dataset_id>/changelog.jsonl \
         --dataset-id <dataset_id> --operation-id <CL0XX> \
         --description "<what was done>" --operator "<agent or human name>" \
         --task-source "tasks.md#<CL0XX>" \
         --input-ref "<path/version of input>" --output-ref "<path/version of output>" \
         --reversible true --notes "<anything relevant>"
     ```
   - Mark the task `[X]` in `tasks.md`.

3. **Final validation.** Run:
   ```
   python scripts/validate_against_model.py validate-dataset <cleaned output> \
       --model instances/<name>/target-data-model.md \
       --out instances/<name>/datasets/<dataset_id>/validation-report.md
   ```
   Every failure must be resolved or explicitly flagged per the constitution's escalation
   rule (recorded in the changelog notes) — implementation is not complete with silent,
   unexplained validation failures.

4. **Verify the changelog chain** before finishing:
   ```
   python scripts/changelog.py verify instances/<name>/datasets/<dataset_id>/changelog.jsonl
   ```

5. **Update the registry.**
   ```
   python scripts/stage_gate.py set-artifact instances/<name>/registry/<dataset_id>.yaml \
       --stage implement --path instances/<name>/datasets/<dataset_id>/validation-report.md
   ```
   Status stays `draft` — implementation done is not the same as signed off.

6. **Report and stop.** Summarize tasks completed, validation status, any flagged
   exceptions, and tell the user final sign-off closes the loop:
   ```
   python scripts/stage_gate.py approve instances/<name>/registry/<dataset_id>.yaml --stage implement --by <name>
   ```
