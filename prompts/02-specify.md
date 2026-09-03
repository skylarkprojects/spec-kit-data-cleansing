---
description: Produce a dataset spec — what it is, its provenance, and what "done" means — read against target-data-model.md. No column-mapping detail.
---

## User Input

The instance name and `dataset_id` for a dataset whose audit stage is approved.

## Precondition

```
python scripts/stage_gate.py check instances/<name>/registry/<dataset_id>.yaml --stage specify
```

If this reports `BLOCKED`, stop and tell the user the audit stage needs approval first
(`01-audit.md`'s last step).

## Steps

1. **Load context**: `instances/<name>/constitution.md`,
   `instances/<name>/target-data-model.md`, and
   `instances/<name>/datasets/<dataset_id>/audit-report.md`.

2. **Write the spec** at `instances/<name>/datasets/<dataset_id>/spec.md` using
   `templates/spec.template.md`:
   - **What this dataset is**, in plain terms, from the audit findings.
   - **Provenance**: source, acquisition date, owner, license/rights, prior processing.
   - **Scope**: what this cleansing effort covers and explicitly excludes.
   - **Definition of done**, stated against `target-data-model.md`'s required fields and
     vocabularies — e.g. "every record has a populated, vocabulary-valid value for field
     X" — without yet saying *which source column* becomes field X. That's `03-plan.md`.
   - **Open questions**: anything that affects scope or the definition of done and can't
     be resolved from the audit report alone. Limit to what's genuinely blocking — make an
     informed default and note it as an assumption instead, where a reasonable one exists.

3. **Resolve open questions with the user** before finalizing, the same way you would
   clarify requirements — present each as a specific question with your best-guess default,
   not an open-ended prompt. Do not proceed to registry update with unresolved open
   questions still marked unresolved.

4. **Update the registry.**
   ```
   python scripts/stage_gate.py set-artifact instances/<name>/registry/<dataset_id>.yaml \
       --stage specify --path instances/<name>/datasets/<dataset_id>/spec.md
   ```

5. **Report and stop.** Summarize scope and the definition of done; tell the user this
   stage needs approval before `03-plan.md`:
   ```
   python scripts/stage_gate.py approve instances/<name>/registry/<dataset_id>.yaml --stage specify --by <name>
   ```
