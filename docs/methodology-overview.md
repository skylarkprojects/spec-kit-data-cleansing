# Methodology Overview

Spec-driven data cleansing applies the constitution → specify → plan → tasks → implement
discipline (originally built for software features) to the problem of bringing a raw
dataset into compliance with a target data model. It is domain-agnostic: nothing in
`/templates`, `/prompts`, or `/scripts` knows what the target schema is, what the raw data
looks like, or what vocabulary it uses. All of that lives in an instance, under
`instances/<name>/`.

## The six artefacts

1. **`constitution.md`** — the project's non-negotiable rules: raw-source immutability,
   transformation logging/reversibility, how ambiguous values are handled, provenance and
   audit requirements, who approves each stage, and the escalation rule for when a
   dataset can't meet a rule (flag vs. block). Written once per instance, amended rarely.
2. **`target-data-model.md`** — the schema every cleaned dataset must align to: required
   and optional fields, controlled vocabularies, field-level validation rules, known
   deviations from the base standard. Also written once per instance; carries a
   machine-readable YAML block the scripts validate against directly.
3. **`audit-report.md`** (per dataset) — a take-stock pass over one raw dataset: column
   inventory, null rates, detected formats, apparent structure. No cleaning, no mapping
   decisions.
4. **`spec.md`** (per dataset) — what the dataset is, its provenance, and what "done"
   means for it, read against the target data model. Still no column-level detail.
5. **`plan.md`** (per dataset) — the field-by-field mapping, the transformation list, and
   a gap/risk assessment against the target model.
6. **`tasks.md`** (per dataset) — the plan broken into discrete, independently verifiable
   cleaning operations, each with its own validation check.

Implementation (`05-implement.md`) executes only what's in an *approved* `tasks.md`,
logging every operation to an append-only, hash-chained changelog.

## The stage-gate rule

A stage's artefact existing is not the same as it being approved. Each dataset has one
registry entry (`instances/<name>/registry/<dataset_id>.yaml`, shaped by
`registry/schema.yaml`) recording an explicit `status: draft | approved | rejected` per
stage. `scripts/stage_gate.py check --stage <next>` is the mechanical gate: it refuses to
let a prompt proceed unless the *prior* stage's status is `approved`, not merely present.
Advancing a stage without running the gate check is a process violation, not a shortcut.

## Where to start

Run `prompts/00-init.md` first, always. It interviews you to produce a complete
`constitution.md` and `target-data-model.md` for your project and won't call
initialisation done until `scripts/validate_against_model.py check-completeness` passes on
both. Only then does `prompts/01-audit.md` accept a raw dataset, and the
audit → specify → plan → tasks → implement sequence proceeds one approval at a time.

See `MIGRATION.md` at the repository root for how this structure relates to the original
spec-kit software-delivery commands it was generalised from.
