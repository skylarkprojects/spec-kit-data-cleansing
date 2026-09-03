<!--
SYNC IMPACT REPORT
==================
Fill this comment in whenever the constitution changes:
Version change: OLD → NEW
Modified principles: (old title → new title, if renamed)
Added sections / Removed sections
Follow-up TODOs
-->

# [PROJECT_NAME] Data Cleansing Constitution

This constitution governs how raw datasets are audited, specified, planned, cleaned, and
approved under the spec-driven data cleansing methodology for **[PROJECT_NAME]**. It is
binding on every dataset that passes through `01-audit.md` → `05-implement.md`. Where a
dataset cannot meet a principle here, the escalation rule below decides whether work is
flagged or blocked — silent deviation is never acceptable.

## Core Principles

### I. Raw Source Immutability (NON-NEGOTIABLE)

- Raw source files, once ingested, MUST NOT be edited, overwritten, or deleted in place.
  [DESCRIBE_RAW_STORAGE_CONVENTION: e.g. raw files live under `raw/<dataset_id>/` and are
  read-only after intake]
- Every cleaning operation reads from a raw or previously-derived artifact and writes a
  **new** artifact; it never mutates its input.
- [ADD_PROJECT_SPECIFIC_IMMUTABILITY_RULES, e.g. checksum verification on ingest]

### II. Reversibility & Transformation Logging (NON-NEGOTIABLE)

- Every transformation applied to a dataset MUST be logged via `scripts/changelog.py`
  before it is considered complete — no undocumented edits.
- Each log entry MUST capture: what changed, why, which task it satisfies, the operator
  (human or agent) who ran it, and enough information to reconstruct or reverse the change.
- [DEFINE_REVERSIBILITY_STANDARD: e.g. every transformation must be re-derivable from the
  raw source plus the changelog alone, without any other state]

### III. Handling of Ambiguous or Uncertain Values

- [DEFINE_AMBIGUITY_POLICY: e.g. values that cannot be confidently mapped to the target
  data model MUST be left null and flagged, never guessed]
- [DEFINE_CONFIDENCE_THRESHOLD_OR_REVIEW_RULE, if applicable]
- Ambiguous values and the reasoning for each decision MUST be recorded in the dataset's
  plan.md or changelog — not silently resolved.

### IV. Provenance & Audit Requirements

- Every dataset registry entry MUST record its source, acquisition date, and owner.
- [DEFINE_PROVENANCE_CHAIN_REQUIREMENTS: e.g. every derived field must be traceable to the
  source column(s) and transformation(s) that produced it]
- [DEFINE_AUDIT_RETENTION_POLICY: how long changelogs and superseded artifacts are kept]
- [DEFINE_LICENSING_OR_RIGHTS_TRACKING_REQUIREMENTS, if applicable]

## Approval Gates

Each stage produces exactly one artifact and requires an explicit human approval before
the next stage may begin. "Present" is not "approved" — approval MUST be recorded as an
explicit `status: approved` on the corresponding stage in the dataset's registry entry
(see `registry/schema.yaml`), together with who approved it and when.

| Stage | Artifact | Approval gate |
|---|---|---|
| audit | audit-report.md | [DEFINE_WHO_APPROVES_AUDIT, e.g. dataset owner] |
| specify | spec.md | [DEFINE_WHO_APPROVES_SPEC] |
| plan | plan.md | [DEFINE_WHO_APPROVES_PLAN, e.g. also requires target-data-model sign-off] |
| tasks | tasks.md | [DEFINE_WHO_APPROVES_TASKS] |
| implement | changelog + validation report | [DEFINE_WHO_APPROVES_IMPLEMENTATION] |

`scripts/stage_gate.py` enforces this mechanically: it refuses to let a stage's prompt
proceed unless the prior stage's status is `approved` in the registry.

## Escalation Rule: Flag vs. Block

When a dataset cannot meet a principle in this constitution:

- **Flag** (proceed with a recorded exception) when: [DEFINE_FLAG_CONDITIONS, e.g. the
  violation is isolated to a small, documented subset of records and does not affect the
  fields the target model marks as required]
- **Block** (stage gate refuses to advance) when: [DEFINE_BLOCK_CONDITIONS, e.g. a
  NON-NEGOTIABLE principle — raw immutability or transformation logging — would be
  violated, or a required target-model field cannot be populated at all]
- All flagged exceptions MUST be recorded in the dataset's plan.md (Gaps & Risks section)
  or changelog with the reasoning, and MUST be visible to whoever approves the next stage.
- [DEFINE_ESCALATION_PATH: who is notified when a block occurs and cannot be resolved by
  the dataset owner alone]

## Governance

- **Authority**: This constitution supersedes ad-hoc convention. `stage_gate.py` and every
  prompt in `/prompts` treat a MUST principle here as a hard gate; conflicts are resolved
  by changing the dataset's plan or tasks, not by diluting a principle.
- **Amendments**: Changes to this document require [DEFINE_AMENDMENT_PROCESS] and a
  version bump per the policy below, recorded in the Sync Impact Report at the top of this
  file.
- **Versioning policy (SemVer for governance)**: MAJOR = backward-incompatible governance
  or principle removal/redefinition; MINOR = a new principle/section or materially
  expanded guidance; PATCH = clarifications and non-semantic refinements.
- **Compliance review**: [DEFINE_WHO_REVIEWS_COMPLIANCE_AND_HOW_OFTEN]

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
