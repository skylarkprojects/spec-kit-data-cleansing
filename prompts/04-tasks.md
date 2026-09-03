---
description: Break the approved plan into discrete, independently verifiable cleaning operations.
---

## User Input

The instance name and `dataset_id` for a dataset whose plan stage is approved.

## Precondition

```
python scripts/stage_gate.py check instances/<name>/registry/<dataset_id>.yaml --stage tasks
```

## Steps

1. **Load** `instances/<name>/datasets/<dataset_id>/plan.md`.

2. **Write `tasks.md`** at `instances/<name>/datasets/<dataset_id>/tasks.md` using
   `templates/tasks.template.md`:
   - Every transformation row in `plan.md` becomes one or more tasks, using the required
     `- [ ] [CL0XX] [P?] Description — targets: ... — source: ...` checklist format.
   - Order tasks so that fields other transformations depend on (e.g. a parsed date used
     to derive another field) come before their dependents; mark independent tasks `[P]`.
   - Every task gets an explicit **validation** line: how to confirm it worked, ideally as
     a check that can run against the data (a count, a regex, a vocabulary membership
     check) rather than "looks right."
   - Include a final validation phase that always runs
     `validate_against_model.py validate-dataset`, plus any dataset-specific cross-field
     checks the plan called for.
   - A task must never require a new scope or schema decision — if generating tasks
     surfaces one, stop and send it back to `plan.md` rather than deciding it here.

3. **Update the registry.**
   ```
   python scripts/stage_gate.py set-artifact instances/<name>/registry/<dataset_id>.yaml \
       --stage tasks --path instances/<name>/datasets/<dataset_id>/tasks.md
   ```

4. **Report and stop.** Summarize task count, how many are parallelizable, and tell the
   user this stage needs approval before `05-implement.md`:
   ```
   python scripts/stage_gate.py approve instances/<name>/registry/<dataset_id>.yaml --stage tasks --by <name>
   ```
