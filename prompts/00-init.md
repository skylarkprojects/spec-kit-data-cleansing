---
description: Interview the user to stand up a new instance — a filled-in constitution.md and target-data-model.md — before any dataset touches 01-audit.md.
---

## Goal

Every project using this methodology needs its own `constitution.md` (data handling
rules, provenance requirements, approval gates, escalation policy) and
`target-data-model.md` (the schema every cleaned dataset must align to) before any dataset
work begins. This prompt interviews the user until both files are fully resolved — no
`[PLACEHOLDER]` tokens, no `TODO(...)` markers — and refuses to call initialisation
complete until `scripts/validate_against_model.py check-completeness` passes on both.

This prompt writes only inside `instances/<name>/`. It never touches `/templates`,
`/prompts`, or `/scripts`.

## Steps

1. **Establish the instance.**
   - Ask for a short, filesystem-safe instance name (e.g. `acme-customer-data`) if not
     already given.
   - Create `instances/<name>/` with subdirectories `registry/` and `datasets/`, if they
     don't exist.
   - Copy `templates/constitution.template.md` → `instances/<name>/constitution.md` and
     `templates/target-data-model.template.md` → `instances/<name>/target-data-model.md`,
     unless they already exist (re-running this prompt should resume, not overwrite).

2. **Interview for `target-data-model.md` first.** Knowing the target shapes what the
   constitution needs to say about it. Ask, section by section, only for what's still a
   placeholder:
   - Target schema/standard: name, version, authoritative source, and how much of it is
     actually in scope for this project.
   - Required fields: for each, name, type, and what it means. Push for precision — "a
     date" is not enough, ask format and whether it's the standard's field or a
     project-specific addition.
   - Optional fields, and the condition under which each should be populated.
   - Controlled vocabularies: for each field constrained to a fixed list, where the list
     comes from and how it's kept current. If the list is short, ask for it inline; if
     long, ask for a file path or URL to load it from.
   - Field-level validation rules beyond required/vocabulary: formats, ranges, cross-field
     consistency.
   - Known extensions or deviations from the base standard, and why.
   - As answers come in, fill in both the prose sections **and** the
     `## Machine-Readable Summary` YAML block at the bottom — they must describe the same
     model. The YAML block is what `scripts/validate_against_model.py` actually checks.

3. **Interview for `constitution.md`.**
   - Raw source immutability: where raw files live, and any project-specific rules beyond
     "never edit in place."
   - Reversibility & transformation logging: what a changelog entry must capture, and any
     reversibility standard beyond "re-derivable from raw + changelog."
   - Handling of ambiguous or uncertain values: the default policy (e.g. null-and-flag
     versus best-guess-and-flag), and any confidence threshold.
   - Provenance & audit requirements: what must be traceable, and retention policy.
   - Approval gates: for each of the five stages (audit, specify, plan, tasks, implement),
     who is authorized to approve it.
   - Escalation rule: concretely, what makes a violation a **flag** versus a **block**, and
     who is notified when a block can't be resolved by the dataset owner alone.
   - Amendment process and compliance review cadence for the constitution itself.

4. **Prefer informed defaults over open-ended questions** where the answer doesn't change
   scope — e.g. propose ISO 8601 for dates, propose that raw files live under `raw/`,
   propose SemVer for constitution versioning — and let the user simply confirm or
   override rather than answering from a blank page. Reserve real questions for decisions
   that materially change what "done" means (required fields, vocab sources, escalation
   policy).

5. **Validate before declaring done.** Run, and show the output of:
   ```
   python scripts/validate_against_model.py check-completeness instances/<name>/constitution.md
   python scripts/validate_against_model.py check-completeness instances/<name>/target-data-model.md
   python scripts/validate_against_model.py check-model instances/<name>/target-data-model.md
   ```
   If any of the three fail, that is the list of what's still missing — go back to step 2
   or 3 for those items. Do not tell the user initialisation is complete, and do not
   suggest running `01-audit.md`, until all three pass.

6. **Report.** Once all three checks pass, summarize: instance path, target schema
   name/version, count of required/optional fields, count of vocabularies, and the
   approval-gate owners recorded. Point to `01-audit.md` as the next step, and note that it
   takes a raw dataset file as input.
