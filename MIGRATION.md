# Migration: Spec-Driven Development → Spec-Driven Data Cleansing

This fork converts the spec-kit methodology (constitution → specify → plan → tasks →
implement, built for software features) into a generic, domain-agnostic spec-driven
**data cleansing** methodology. Nothing in the new package knows about any specific target
schema, vocabulary, or dataset shape — all of that is supplied per-project under
`instances/<name>/`.

## New top-level structure

```text
/templates       constitution / target-data-model / spec / plan / tasks templates
/prompts         00-init.md … 05-implement.md
/scripts         profile_dataset.py, validate_against_model.py, changelog.py, stage_gate.py
/registry        schema.yaml + README for the per-dataset registry entry format
/instances       README + an empty example stub — no real project content ships here
/docs            methodology-overview.md
MIGRATION.md      this file
```

See `docs/methodology-overview.md` for how the six artefacts and the stage-gate rule fit
together.

## Renamed / generalized (old → new)

| Original | Became | What changed |
|---|---|---|
| `.specify/memory/constitution.md` (the ratified spec-kit-for-itself constitution) | `templates/constitution.template.md` | Kept the shape (principles, governance, versioning policy) but replaced every software-specific principle (code architecture, pytest matrix, CLI verb conventions, offline-first performance) with placeholder sections for data handling rules: raw immutability, transformation reversibility/logging, ambiguous-value handling, provenance/audit, approval gates, and a flag-vs-block escalation rule. |
| `templates/commands/specify.md` | `templates/spec.template.md` + `prompts/02-specify.md` | Split the artefact (what "done" means for a dataset, read against `target-data-model.md`) from the interview/generation logic. Dropped the feature-branch/git-numbering machinery and the "user stories with P1/P2/P3 priorities" framing — a dataset spec doesn't have user stories. |
| `templates/commands/plan.md` | `templates/plan.template.md` + `prompts/03-plan.md` | Replaced "Technical Context / research.md / data-model.md / contracts/" (software architecture artefacts) with field-by-field mapping, transformation list, controlled-vocabulary reconciliation, and a gap/risk assessment scored flag-vs-block against the constitution. |
| `templates/commands/tasks.md` | `templates/tasks.template.md` + `prompts/04-tasks.md` | Replaced "tasks organized by user story (P1/P2/P3) with Setup/Foundational/Polish phases" with tasks organized by target field/transformation, each carrying its own data-level validation check instead of a test-suite reference. |
| `templates/commands/implement.md` | `prompts/05-implement.md` | Replaced ignore-file generation, TDD/test-suite execution, and "models/services/endpoints" language with: execute only approved tasks against a working copy (never raw), log every operation via `changelog.py`, run `validate_against_model.py`, and hard-refuse if `tasks.md` isn't approved. |
| *(no direct equivalent — see below)* | `prompts/00-init.md` | New. Nothing in the original workflow stood up project-level governance before the first feature; data cleansing needs a target schema defined before any dataset work starts. |
| *(no direct equivalent)* | `prompts/01-audit.md` | New. The original had no "take stock of raw input before deciding what to build" stage — features are specified from a description, not profiled from a file. |
| `templates/commands/clarify.md` | *(folded in, not a standalone prompt)* | Its open-questions loop lives on inside `02-specify.md` ("Open Questions" section, resolved with the user before the registry is updated) rather than as a separate five-question command — a dataset spec has far fewer open dimensions than a feature spec. |
| `extensions/bug/*` (assess/fix/test a bug against source code) | `extensions/issue/*` (assess/resolve/verify a data quality issue against a dataset) | Same three-stage shape and the same guardrails (URL trust policy, no-overwrite-without-confirmation, never over-claim `verified`), retargeted from "code paths and tests" to "plan.md mappings, tasks.md operations, and changelog entries." Storage moved from `.specify/bugs/<slug>/` to `instances/<name>/datasets/<dataset_id>/issues/<slug>/`. |
| `extensions/assess/*` (5-stage idea assessment: intake/research/define/shape/decide) | `extensions/intake/*` (3-stage: capture/assess/decide) | Trimmed to three stages — a candidate dataset needs a rights/redundancy/fit check, not a full product-idea funnel with market research and concept-shaping. A `go` verdict now calls `scripts/stage_gate.py init-dataset` directly instead of handing off free-text to a `/speckit.specify` command. |

## Newly created (no prior equivalent)

- `registry/schema.yaml` and `registry/README.md` — the original had no concept of a
  machine-checked "is this artefact actually approved" gate; `Approved`/`Present` were
  conflated (a file existing was the only signal `implement.md` checked via
  `check-prerequisites.py`). The registry makes approval an explicit, per-stage status.
- `scripts/stage_gate.py` — enforces the registry-based gate mechanically; there was no
  analogue (the original's `check-prerequisites.py` scripts only checked file existence).
- `scripts/profile_dataset.py` — a domain-agnostic column/null-rate/format profiler; the
  original workflow had nothing that inspects raw data at all, since it starts from a
  natural-language feature description, not a file.
- `scripts/validate_against_model.py` — validates artefact completeness (no leftover
  `[PLACEHOLDER]` tokens) and validates a cleaned dataset against the target model's
  machine-readable YAML block. No equivalent existed; the closest analogue,
  `/speckit.analyze`, checks spec/plan/tasks consistency against each other and the
  constitution, not a dataset against an external schema.
- `scripts/changelog.py` — an append-only, hash-chained operation log. The original relied
  on git history and PR descriptions for change provenance; a data cleansing pipeline
  needs per-transformation, per-record-scope provenance that git history alone doesn't
  capture.
- `instances/` as a concept — the original had no separation between "the tool" and "a
  specific project's filled-in governance," since the constitution lived in-repo at
  `.specify/memory/constitution.md` for the one project spec-kit governs (itself).

## Dropped, with reasoning

- **`templates/commands/analyze.md`** (cross-artefact consistency report over
  spec/plan/tasks) — not carried forward as a standalone prompt. Its job is now split
  across `scripts/validate_against_model.py` (mechanical field/vocabulary consistency) and
  the stage-gate approval step (a human reviewing plan.md against spec.md before
  approving). A read-only "diff the three markdown files and guess at drift" pass added
  less value once the target model is itself machine-checkable.
- **`templates/commands/checklist.md`** ("unit tests for English" — requirements-quality
  checklists) — dropped. Its core insight (validate the *requirements*, not the
  implementation) is preserved as the Definition of Done checklist built into
  `templates/spec.template.md`, but a dataset spec's requirements are narrow enough
  (field-level, read against one fixed target model) that a separate custom-checklist
  generator wasn't worth carrying forward as its own prompt.
- **`templates/commands/converge.md`** (assess the codebase against spec/plan/tasks and
  append remaining work as new tasks) — dropped. It exists to close the gap between
  *code* and *intent* after an implementation pass on a live, evolving codebase. A dataset
  cleaning run is closed-ended (once `validate_against_model.py` passes, the dataset is
  done); a stuck or partially-done run is better handled by `extensions/issue/` (assess
  what's still wrong, resolve it, verify it) than by an automatic gap-scanner.
- **`templates/commands/taskstoissues.md`** (convert `tasks.md` into GitHub issues) —
  dropped as a core prompt. GitHub issue tracking is a delivery-process choice orthogonal
  to data cleansing; nothing about it needed generalizing, and keeping it would have
  implied every instance uses GitHub. A project that wants this can still use it as-is
  from `templates/commands/taskstoissues.md`, unmodified.

## What was left untouched, and why

`src/specify_cli/`, `extensions/agent-context/`, `extensions/git/`, `extensions/template/`,
`extensions/selftest/`, `presets/`, `workflows/`, `bundler/`, and `tests/` are the CLI
packaging/distribution layer — how spec-kit installs itself and its command files into a
coding agent's environment (Claude Code, Copilot, etc.), independent of what those command
files say. That layer is domain-agnostic already: it doesn't know or care whether the
commands it installs describe building software or cleaning data. The two new extensions
(`extensions/issue/`, `extensions/intake/`) are delivered *through* that same mechanism —
proof that generalizing the content didn't require rewriting the delivery machinery.
`extensions/bug/` and `extensions/assess/` were **not deleted**; they were generalized into
`issue/` and `intake/` respectively (see the table above) and marked `"bundled": false` in
`extensions/catalog.json` rather than removed, in case a downstream instance still wants
the original software-triage workflow alongside the data one.

`templates/commands/*.md` (the original six-command set, still wired into the CLI's
bundled `core_pack`) and `templates/{constitution,spec,plan,tasks,checklist}-template.md`
were likewise left in place rather than deleted — they're what `specify init` still
installs for a software project using this fork's underlying CLI. The new,
data-cleansing-specific artefacts live alongside them as a separate, self-contained layer
(`/templates`, `/prompts`, `/scripts`, `/registry`, `/instances`, `/docs`) that a data
project uses directly (e.g. pasted into Claude Code per `prompts/00-init.md`) without
going through `specify init` at all.
