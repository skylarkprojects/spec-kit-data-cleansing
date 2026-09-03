# Cleaning Tasks: [DATASET_NAME]

**Dataset ID**: [DATASET_ID] | **Plan**: [LINK_TO_PLAN_MD]
**Created**: [DATE]

Each task is one discrete, independently verifiable cleaning operation. `05-implement.md`
executes these in order (respecting dependencies), logs each one via `changelog.py` as it
completes it, and marks it `[X]` when done. A task must be specific enough to run without
re-reading the plan.

## Checklist Format (required)

```text
- [ ] [TaskID] [P?] Description — targets: <field(s)> — source: <transformation ID from plan.md>
```

- **Task ID**: sequential, `CL001`, `CL002`, …
- **[P]**: include only if this task can run in parallel with others in the same phase
  (independent fields, no shared state)
- **Description**: one imperative sentence naming the exact operation
- Every task MUST trace back to a transformation row in `plan.md` (or a validation step)

## Phase 1: Setup

- [ ] [CL001] [DESCRIPTION — e.g. load raw source into working copy, verify checksum against registry raw_path]

## Phase 2: Field Transformations

One phase section per target field or logical group of fields, ordered so that fields
other transformations depend on come first.

### [TARGET_FIELD_GROUP]

- [ ] [CL00X] [P] [DESCRIPTION] — targets: [FIELD] — source: [plan.md transformation ID]
  - **Validation**: [HOW_TO_CONFIRM_THIS_TASK_SUCCEEDED, e.g. "0 rows where field is
    non-null and outside the controlled vocabulary"]

## Phase 3: Cross-Field & Whole-Dataset Validation

- [ ] [CL0XX] Run `scripts/validate_against_model.py validate-dataset` against the cleaned
      output; resolve or flag every failure per the constitution's escalation rule.
- [ ] [CL0XX] [ADD_DATASET_SPECIFIC_CROSS_FIELD_CHECKS]

## Phase 4: Sign-Off

- [ ] [CL0XX] Produce the final validation report and update the registry entry's
      `implement` stage to `draft` with the changelog path, ready for approval.

## Dependencies

- [DESCRIBE_ANY_TASK_ORDERING_CONSTRAINTS_BEYOND_PHASE_ORDER]

## Notes

- Tasks in this file are cleaning-operation tasks, not general project tasks — no task
  here should require a schema or scope decision; those belong in `plan.md`. If executing
  a task surfaces a scope question, stop and route it back to `plan.md` rather than
  deciding it inline.
