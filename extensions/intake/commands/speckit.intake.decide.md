---
description: "Apply a go / needs-clarification / kill gate; a go registers the dataset and hands off to 01-audit.md"
---

# Decide: Go, Clarify, or Kill

Render the verdict on a candidate dataset and record it at
`instances/<name>/intake/<slug>/decision.md`. A **go** registers the dataset in the
registry and hands off to `01-audit.md`; a **kill** stops it with a documented reason;
**needs-clarification** sends it back to `capture` or `assess`. Killing a candidate here,
with a clear reason, is a successful outcome — it's the whole point of this gate.

## User Input

```text
$ARGUMENTS
```

Resolve `INTAKE_SLUG` the same way as the other `intake` commands.

## Prerequisites

- `INTAKE_DIR/fit.md` MUST exist (you cannot decide without a fit assessment). If missing,
  point to `__SPECKIT_COMMAND_INTAKE_ASSESS__`.
- Read `intake.md` and `fit.md` in full.
- If `INTAKE_DIR/decision.md` already exists, ask before overwriting (interactive) or
  refuse (automated).

## Execution

1. **Reach a verdict**, consistent with `fit.md`'s ratings:
   - **go** — rights are clear (or clear enough to proceed while resolving a minor
     detail), redundancy is acceptable, and there's no evident quality ceiling that makes
     the target model's required fields unreachable. Effort/risk being high is not by
     itself a reason to kill — that's what `03-plan.md`'s gap/risk assessment is for.
   - **needs-clarification** — rights or fit are genuinely unresolved and material. Name
     exactly what's missing and which stage to revisit.
   - **kill** — rights are unavailable, the data is fully redundant with an existing
     approved dataset, or the quality ceiling makes the target model's required fields
     structurally unreachable. State the decisive reason plainly.

2. **On `go`, register the dataset** rather than describing it as a future step:
   ```
   python scripts/stage_gate.py init-dataset instances/<name>/registry/<dataset_id>.yaml \
       --dataset-id <dataset_id> --name "<name>" --source "<from intake.md>" \
       --owner "<owner>" --raw-path "<path to raw file once ingested per the constitution>" \
       --changelog-path "instances/<name>/datasets/<dataset_id>/changelog.jsonl"
   ```
   Derive `<dataset_id>` from `INTAKE_SLUG` unless the user specifies otherwise.

3. **Write `decision.md`**:

   ```markdown
   # Intake Decision: <short title>

   - **Slug**: <INTAKE_SLUG>
   - **Decided**: <ISO 8601 date>
   - **Verdict**: go | needs-clarification | kill
   - **Dataset ID** (if go): <dataset_id>

   ## Rationale

   <The call and why, referencing fit.md.>

   ## If needs-clarification

   - **Blocking questions**: [NEEDS CLARIFICATION: …]
   - **Revisit stage**: capture | assess

   ## If go — Handoff to 01-audit.md

   - **Dataset ID**: <dataset_id>
   - **Registry entry**: `instances/<name>/registry/<dataset_id>.yaml`
   - **Raw file location**: <path>
   ```

4. **Report back** with the slug, the verdict, and the next step:
   - **go** → `01-audit.md` using the registered `dataset_id`.
   - **needs-clarification** → re-run the named stage.
   - **kill** → none; the record remains for future reference.

## Guardrails

- Only a `go` verdict writes outside `instances/<name>/intake/<slug>/` — and only to
  create the registry entry via `stage_gate.py init-dataset`, never by hand-editing the
  YAML.
- Never pre-empt `01-audit.md` — a `go` only registers the dataset; it does not profile or
  audit it.
- Never overwrite an existing `decision.md` without confirmation.
