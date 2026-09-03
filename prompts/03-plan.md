---
description: Produce the field-by-field mapping, transformation list, and gap/risk assessment against target-data-model.md.
---

## User Input

The instance name and `dataset_id` for a dataset whose specify stage is approved.

## Precondition

```
python scripts/stage_gate.py check instances/<name>/registry/<dataset_id>.yaml --stage plan
```

## Steps

1. **Load context**: `instances/<name>/target-data-model.md`,
   `instances/<name>/datasets/<dataset_id>/spec.md`, and the audit report.

2. **Write the plan** at `instances/<name>/datasets/<dataset_id>/plan.md` using
   `templates/plan.template.md`:
   - **Field-by-field mapping**: every target field (required and optional) mapped to a
     source column, a derivation (multiple source columns, a split, a computed value), or
     explicitly "no source — leave null." Every target field must appear, even the
     unmapped ones.
   - **Transformations**: one row per distinct operation (parsing, trimming, unit
     conversion, format normalization, vocabulary reconciliation). Give each a stable ID —
     `04-tasks.md` will turn these into tasks.
   - **Controlled vocabulary reconciliation**: for every field bound to a vocabulary in
     `target-data-model.md`, how raw values get reconciled — exact match, lookup table, or
     match-plus-review — and what happens to a value that doesn't reconcile.
   - **Gaps & risks**: everything that keeps the dataset from cleanly meeting the target
     model. For each, classify **flag or block** per the constitution's escalation rule —
     don't leave this undecided.
   - **Out-of-model data**: source columns with no target-model home; decide drop, retain
     as an extension field, or retain in a side artifact, and say why.
   - **Validation strategy**: what `05-implement.md` will run to confirm the plan actually
     worked (always includes `validate_against_model.py validate-dataset`).

3. **Check every "block" gap against the constitution before finalizing.** If a block gap
   has no viable mitigation, stop and tell the user this dataset cannot proceed to
   `04-tasks.md` as scoped — that's a decision for the dataset owner, not something to plan
   around silently.

4. **Update the registry.**
   ```
   python scripts/stage_gate.py set-artifact instances/<name>/registry/<dataset_id>.yaml \
       --stage plan --path instances/<name>/datasets/<dataset_id>/plan.md
   ```

5. **Report and stop.** Summarize mapping coverage (X of Y target fields mapped), flagged
   vs. blocked gaps, and tell the user this stage needs approval before `04-tasks.md`:
   ```
   python scripts/stage_gate.py approve instances/<name>/registry/<dataset_id>.yaml --stage plan --by <name>
   ```
