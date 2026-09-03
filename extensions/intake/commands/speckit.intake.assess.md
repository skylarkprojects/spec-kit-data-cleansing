---
description: "Assess a captured dataset's fit against the target data model, rights, and redundancy with the existing registry"
---

# Assess Candidate Dataset Fit

Weigh whether a captured candidate dataset is worth carrying through the full cleansing
pipeline. Output: `instances/<name>/intake/<slug>/fit.md`.

Assess **judges fit; it does not clean or map fields.** No column-by-column mapping — that
only happens in `03-plan.md`, after a `go` verdict.

## User Input

```text
$ARGUMENTS
```

Resolve `INTAKE_SLUG` the same way as `__SPECKIT_COMMAND_INTAKE_CAPTURE__`: explicit →
conversation context (confirmed by `intake/<slug>/intake.md` existing) → single candidate
on disk → ask (interactive) / stop and list candidates (automated).

## Prerequisites

- `INTAKE_DIR/intake.md` MUST exist — if not, point to
  `__SPECKIT_COMMAND_INTAKE_CAPTURE__`.
- If `INTAKE_DIR/fit.md` already exists, ask before overwriting (interactive) or refuse
  (automated).
- Load `instances/<name>/target-data-model.md`, `instances/<name>/constitution.md`, and
  the existing `instances/<name>/registry/*.yaml` entries.

## Execution

1. **Check rights.** Is there a clear license or usage right to clean and use this data,
   per the constitution's provenance requirements? If unresolved, that alone can force
   `needs-clarification`.

2. **Check redundancy.** Does an existing, already-approved registry entry already cover
   this data (same source, overlapping scope)? If so, note it — duplicating pipeline effort
   needs a deliberate reason, not an oversight.

3. **Check fit against the target model.** If a sample is available, spot-check whether
   the data plausibly contains the target model's required fields (directly or derivably)
   — a quick look, not a full `profile_dataset.py` run (that happens in `01-audit.md`
   after a `go`). If no sample is available, note that fit is unverified.

4. **Estimate effort and risk**, each rated `low | medium | high`:
   - **Mapping effort** — how far the apparent shape is from the target model.
   - **Rights risk** — how solid the usage terms are.
   - **Redundancy risk** — how much this overlaps existing approved datasets.
   - **Quality ceiling** — based on what's visible, is there an obvious reason this data
     can never satisfy the target model's required fields (e.g. a required field simply
     isn't captured anywhere in the source)?

5. **Write `fit.md`**:

   ```markdown
   # Dataset Fit Assessment: <short title>

   - **Slug**: <INTAKE_SLUG>
   - **Assessed**: <ISO 8601 date>
   - **Intake**: ./intake.md

   ## Rights

   <Clear / unclear / [NEEDS CLARIFICATION] — reasoning.>

   ## Redundancy

   <None found / overlaps <registry entry> — reasoning.>

   ## Fit Against Target Model

   <What was checked, what was found, or "unverified — no sample available".>

   ## Effort & Risk

   | Dimension | Rating | Notes |
   |---|---|---|
   | Mapping effort | low/medium/high | … |
   | Rights risk | low/medium/high | … |
   | Redundancy risk | low/medium/high | … |
   | Quality ceiling concern | low/medium/high | … |

   ## Recommendation Leaning

   <go / needs-clarification / kill — with one-sentence reasoning. The actual verdict is
   __SPECKIT_COMMAND_INTAKE_DECIDE__'s call; this is input to it.>
   ```

6. **Report back** with the slug, the fit.md path, and the next step:
   `__SPECKIT_COMMAND_INTAKE_DECIDE__ slug=<INTAKE_SLUG>`.

## Guardrails

- Never write into `registry/` or `datasets/` here.
- Never claim a sample was checked if none was available — say so explicitly.
- Never overwrite an existing `fit.md` without confirmation.
