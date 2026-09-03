# Specification-Driven Data Cleansing

> The deep-dive companion to [`docs/methodology-overview.md`](docs/methodology-overview.md).
> This is the data-cleansing rewrite of upstream Spec Kit's software-delivery essay of the
> same name — see [`MIGRATION.md`](MIGRATION.md) for what changed and why. If you're
> looking for the original *software* methodology this fork is based on, its CLI and
> command templates (`templates/commands/*.md`) still work unmodified; the prose write-up
> of that methodology is preserved in this file's git history.

## The Power Inversion

In most data cleansing efforts, the target schema is aspirational scaffolding. Someone
writes a data dictionary, everyone nods, and then the actual cleaning happens
column-by-column, ad hoc, in whatever tool is fastest — and the dictionary drifts out of
sync with what the data actually became. The schema was guidance; the transformations
were the truth.

Spec-driven data cleansing inverts this. The **target data model becomes the executable
check**: every cleaned record is validated against it mechanically
(`scripts/validate_against_model.py`), not eyeballed against a document someone half-read.
The **plan becomes the traceable record** of every mapping decision, not a memory someone
has to reconstruct later. The **constitution becomes the enforced gate**, not an onboarding
slide. Nothing about a dataset is "probably clean" — it's either validated against the
model, or it's a documented, flagged exception.

## The Pipeline in Practice

```text
00-init.md      → constitution.md + target-data-model.md   (once per project)
01-audit.md     → audit-report.md    (per dataset — take stock, no cleaning)
02-specify.md   → spec.md            (what this dataset is, what "done" means)
03-plan.md      → plan.md            (field-by-field mapping + gap/risk assessment)
04-tasks.md     → tasks.md           (discrete, independently verifiable operations)
05-implement.md → cleaned dataset + changelog.jsonl + validation-report.md
```

Each arrow above is gated: `scripts/stage_gate.py check <registry entry> --stage <next>`
refuses to let the next prompt do anything until the current stage's registry status is
`approved` — not merely `artifact_path` being set. A prompt producing a plausible-looking
`plan.md` that no one has actually reviewed is exactly the failure mode this exists to
prevent.

### Worked Example: A Contact Records Export

Say a project receives a CSV export of customer contact records from an old system, and
the target data model requires a normalized `email`, a `country_code` (ISO 3166-1 alpha-2,
a controlled vocabulary), and a `created_at` (ISO 8601 date).

```text
$ (agent, following 01-audit.md)
> python scripts/profile_dataset.py contacts_export.csv
  - email: 12% blank, no format anomalies detected
  - phone_country: 3% blank, 40 distinct values — mix of "US", "United States", "+1"
  - signup_date: 0% blank, two formats detected: MM/DD/YYYY and YYYY-MM-DD mixed

$ (agent, following 03-plan.md, reading target-data-model.md)
  | Target field   | Source column  | Mapping                                    |
  |----------------|----------------|---------------------------------------------|
  | email          | email          | direct, lowercase + trim                    |
  | country_code   | phone_country  | reconcile free-text/dial-code → ISO alpha-2 |
  | created_at     | signup_date    | parse both formats → ISO 8601               |

  Gap: 40 distinct phone_country values, ~6 don't map cleanly to a country
  ("intl", "unknown", "N/A") → FLAG per constitution (isolated, non-required-field-blocking)
```

Nothing here required knowing anything about "contact records" as a domain — the same
prompts, the same scripts, and the same gate would apply to a sensor-log export or a
product catalog, driven entirely by whatever `target-data-model.md` says for that project.

## Why This Matters Now

AI agents are fast at producing a plausible-looking cleaned dataset from a vague
instruction — and just as fast at silently guessing wrong on the 3% of records that don't
fit the obvious pattern. Three things make that expensive in data cleansing specifically:

- **Silent guesses compound.** A guessed date format or a fabricated country code doesn't
  fail loudly — it looks like data, until someone downstream trusts it.
- **"Looks right" isn't verifiable.** Code has tests; a cleaned CSV doesn't, unless
  something mechanically checks every record against the target model.
- **Provenance decays fast.** Six months later, "why does this field have this value" is
  unanswerable without a changelog — git blame on a notebook doesn't capture per-record
  transformation history.

Structure — a machine-checkable target model, a required registry approval per stage, and
an append-only changelog — is what makes an agent's speed trustworthy instead of merely
fast.

## Core Principles

1. **Raw sources are immutable.** Every transformation reads from raw or a prior derived
   artefact and writes a *new* one. Nothing overwrites raw data in place.
2. **Every transformation is logged and, in principle, reversible.**
   `scripts/changelog.py` chains each entry to the previous one by hash — the log itself
   is tamper-evident, not just append-only by convention.
3. **Ambiguous values are flagged, never guessed.** The constitution's escalation rule
   (flag vs. block) makes this an explicit per-project policy, not an implicit judgment
   call left to whichever agent happens to be running.
4. **Approval is explicit, not inferred from a file existing.** `stage_gate.py` reads a
   `status: approved` field a human set — an artefact's mere presence never advances the
   pipeline.
5. **The target model is the only source of truth for "compliant."** Nothing in
   `/prompts` or `/scripts` hardcodes a schema; everything reads
   `instances/<name>/target-data-model.md`'s machine-readable YAML block at run time.

## Template-Driven Quality: How Structure Constrains an Agent for Better Outcomes

### 1. Preventing Premature Mapping Decisions

`02-specify.md` explicitly forbids column-mapping detail — a spec states what "done"
means against the target model's *fields*, not which *source column* becomes which field.
This forces the "what" (scope, provenance, definition of done) to be settled and approved
before the "how" (the actual mapping) is drafted, the same way a software spec is meant to
stay implementation-agnostic.

### 2. Forcing Explicit Uncertainty Markers

`02-specify.md`'s Open Questions section and the constitution's ambiguity policy both push
toward the same discipline: an unresolved decision gets written down and resolved with a
human, not silently defaulted. A `plan.md` gap gets classified **flag or block** — never
left implicit.

### 3. Structured Validation Instead of "Looks Right"

Every `tasks.md` operation carries its own validation line, and the final phase always
runs `scripts/validate_against_model.py validate-dataset`. This is data cleansing's
analogue to test-first development: the check is written into the task before the
operation is trusted as done.

### 4. Constitutional Compliance Through Gates

`scripts/stage_gate.py` is a mechanical gate, not a style guideline. A `plan.md` with an
unresolved **block** gap is a decision for the dataset owner to make explicitly (per the
constitution's escalation rule) — the pipeline does not let an agent quietly route around
it by approving anyway.

### 5. Hierarchical Detail Management

Detail increases stage by stage: `audit-report.md` describes *what's there*, `spec.md`
describes *what done means*, `plan.md` adds the *field-by-field mapping*, `tasks.md` adds
*execution-level detail*. Each stage reads only what the previous stage decided — a
`tasks.md` task is never the place to relitigate scope.

### 6. Validation-First Thinking

`validate_against_model.py`'s YAML-block contract means the target model's required
fields, vocabularies, and rules are defined once, machine-parseable, and checked
identically at every stage that touches them — `00-init.md`'s completeness check, and
`05-implement.md`'s final validation, run the *same* parser against the *same* block.

## The Constitutional Foundation

`instances/<name>/constitution.md` is not aspirational — it is what `stage_gate.py` and
every prompt treat as a hard gate. Its core principles, filled in per project from
[`templates/constitution.template.md`](templates/constitution.template.md):

- **Raw Source Immutability** — non-negotiable; enforced by convention (every prompt reads
  from a working copy) and by review (a diff touching a raw path is a red flag).
- **Reversibility & Transformation Logging** — non-negotiable; enforced mechanically by
  `changelog.py`'s hash chain, which `05-implement.md` verifies before reporting done.
- **Handling of Ambiguous or Uncertain Values** — a per-project policy, not a global
  default, because what counts as "ambiguous enough to flag" genuinely differs by domain
  and risk tolerance.
- **Provenance & Audit Requirements** — what must be traceable, and for how long.
- **Approval Gates** — who signs off on each of the five stages; enforced by
  `stage_gate.py` reading the registry, not by convention.
- **Escalation Rule (flag vs. block)** — the constitution's answer to "what happens when a
  dataset can't meet a rule," applied consistently across `plan.md`'s gap assessment and
  `05-implement.md`'s validation failures.

### Constitutional Enforcement Through Scripts

Where the constitution states a rule, a script enforces it mechanically wherever
practical, rather than relying on an agent remembering to check:

- `stage_gate.py check` — the approval gate, read from the registry.
- `changelog.py verify` — the reversibility/logging chain, checked for tampering.
- `validate_against_model.py check-completeness` — no dataset work starts against an
  incomplete constitution or target model.
- `validate_against_model.py validate-dataset` — the target model's required fields and
  vocabularies, checked against the actual cleaned output, not just described.

### Constitutional Evolution

A constitution amendment follows the same discipline it enforces on datasets: a version
bump (SemVer — MAJOR for principle removal/redefinition, MINOR for a new principle, PATCH
for clarification), recorded in a Sync Impact Report at the top of the file, per
[`templates/constitution.template.md`](templates/constitution.template.md)'s Governance
section.

## The Transformation

Spec-driven data cleansing isn't a claim that agents write better transformations than
humans. It's a claim that **structure is what makes an agent's transformations
trustworthy**: a machine-checked target model instead of a document someone half-read, an
explicit approval instead of an artefact's mere existence, and a tamper-evident changelog
instead of institutional memory. The six artefacts and the stage gate exist to make that
structure the default, not an afterthought bolted on once something has already gone
wrong.
