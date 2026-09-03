---
description: Take stock of a raw dataset — column inventory, null rates, detected formats, apparent structure. No cleaning, no schema decisions.
---

## User Input

The path to a raw dataset file, and the instance name (`instances/<name>/`) it belongs to.

## Precondition

This prompt refuses to run against an instance whose init isn't complete:

```
python scripts/validate_against_model.py check-completeness instances/<name>/constitution.md
python scripts/validate_against_model.py check-completeness instances/<name>/target-data-model.md
```

If either fails, stop and tell the user to finish `00-init.md` first.

## Steps

1. **Register the dataset.** Derive a short, stable `dataset_id` slug from the file (ask
   the user to confirm or override it). Create the registry entry:
   ```
   python scripts/stage_gate.py init-dataset instances/<name>/registry/<dataset_id>.yaml \
       --dataset-id <dataset_id> --name "<human name>" --source "<where it came from>" \
       --owner "<owner>" --raw-path "<path to raw file, copied under an immutable raw/ location per the constitution>" \
       --changelog-path "instances/<name>/datasets/<dataset_id>/changelog.jsonl"
   ```
   If a raw storage convention is defined in the constitution, follow it — copy the raw
   file into place rather than referencing it where the user happens to have left it,
   since Principle I requires raw sources to be immutable and centrally kept.

2. **Profile it.** Run:
   ```
   python scripts/profile_dataset.py <raw file> --out instances/<name>/datasets/<dataset_id>/profile.json
   ```
   Also generate the markdown form for human review (omit `--out` or use a `.md` path).

3. **Take stock — no cleaning, no schema decisions.** Using the profile output, write
   `instances/<name>/datasets/<dataset_id>/audit-report.md` covering, generically (never in
   terms of a specific domain vocabulary):
   - **Column inventory**: every column, its detected type, null rate, and cardinality.
   - **Detected formats**: what `profile_dataset.py` found per column (dates, numbers,
     booleans, emails, URLs, free text) and any patterns worth flagging (mixed formats
     within one column, suspicious outliers in length or cardinality).
   - **Apparent structure**: describe the shape of the file itself — e.g. does it look
     like one row per real-world entity, or does it mix rows of different kinds (a
     metadata/header table folded into the same file as a detail/observation table)? Are
     there repeated blocks, wide vs. long layout, obvious foreign-key-like columns
     pointing at another file? Describe what's observed in the data's own terms — column
     names, repetition patterns, key-like columns — not in terms of any target schema.
   - **Data quality first impressions**: duplicate rows, columns that are entirely blank,
     columns whose name and content disagree, encoding issues.
   - Explicitly do **not** propose a mapping to the target data model here — that's
     `03-plan.md`'s job. This stage answers "what is actually in this file," not "how does
     it become compliant."

4. **Update the registry.**
   ```
   python scripts/stage_gate.py set-artifact instances/<name>/registry/<dataset_id>.yaml \
       --stage audit --path instances/<name>/datasets/<dataset_id>/audit-report.md
   ```
   Status stays `draft`.

5. **Report and stop.** Summarize row/column counts, the most notable findings, and tell
   the user this stage requires human approval before `02-specify.md` can run:
   ```
   python scripts/stage_gate.py approve instances/<name>/registry/<dataset_id>.yaml --stage audit --by <name>
   ```
