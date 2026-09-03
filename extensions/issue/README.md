# Data Issue Triage Workflow Extension

A three-step triage workflow for data quality issues discovered *after* a dataset has
already been signed off by `05-implement.md`: assess, resolve, verify. Each issue lives in
its own directory under `instances/<name>/datasets/<dataset_id>/issues/<slug>/`.

## Overview

1. **Assess** — read an issue report (pasted text or a URL), judge whether it's a real
   data defect, locate whether the cause is the raw source, the plan's mapping, or a
   specific cleaning task, and propose a remediation.
2. **Resolve** — apply the fix (amend `plan.md`, add/correct a `tasks.md` operation, or
   record a documented exception), executing it against the dataset's working copy and
   logging it via `scripts/changelog.py`.
3. **Verify** — re-check the affected field/records and re-run
   `scripts/validate_against_model.py`, then record the verification result.

```text
instances/<name>/datasets/<dataset_id>/issues/<slug>/
├── assessment.md   # written by speckit.issue.assess
├── resolve.md       # written by speckit.issue.resolve
└── verify.md         # written by speckit.issue.verify
```

## Commands

| Command | Description | Output |
|---|---|---|
| `speckit.issue.assess` | Triages a data issue report against an implemented dataset. | `issues/<slug>/assessment.md` |
| `speckit.issue.resolve` | Applies the remediation and logs it to the changelog. | `issues/<slug>/resolve.md` |
| `speckit.issue.verify` | Validates the fix and records the verification report. | `issues/<slug>/verify.md` |

## Relationship to the Core Pipeline

This extension does not replace `01-audit.md` … `05-implement.md` — it handles defects
found *after* a dataset's `implement` stage is already `approved`. A fix here still goes
through the same constitution (raw immutability, changelog logging, escalation rule) and,
if it changes `plan.md`, the same stage-gate re-approval as the core pipeline.

## Installation

```bash
specify extension add issue
```

## Typical Flow

```bash
# 1. Triage a data quality complaint
/speckit.issue.assess "records with status=UNKNOWN are showing up where the target model requires a controlled-vocabulary value" dataset=widgets-2026-export

# 2. Apply the fix
/speckit.issue.resolve slug=status-unknown-leak

# 3. Verify it actually resolved
/speckit.issue.verify slug=status-unknown-leak
```

## Guardrails

- `speckit.issue.assess` and `speckit.issue.verify` never modify the dataset — read and
  write only inside `issues/<slug>/`.
- `speckit.issue.resolve` is the only command that changes `plan.md`, `tasks.md`, or the
  dataset's cleaned output, and every change it makes is logged via `changelog.py`.
- Results are never over-claimed: a fix that wasn't actually re-checked against the
  original symptom is reported `partial`, not `verified`.

## Hooks

This extension registers no hooks. The three commands are always invoked explicitly.
