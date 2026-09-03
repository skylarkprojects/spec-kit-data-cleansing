# Dataset Spec: [DATASET_NAME]

**Dataset ID**: [DATASET_ID] | **Registry entry**: `registry/[DATASET_ID].yaml`
**Created**: [DATE] | **Audit report**: [LINK_TO_AUDIT_REPORT]

> Written against `target-data-model.md`. Do not include field-by-field column mappings
> here — that belongs in `plan.md`.

## What This Dataset Is

[1-2 paragraphs: what real-world thing this dataset represents, who produced it, and what
it is meant to be used for downstream.]

## Provenance

| | |
|---|---|
| Source | [WHERE_IT_CAME_FROM] |
| Acquired | [DATE] |
| Owner / point of contact | [NAME_OR_TEAM] |
| License / rights | [LICENSE_OR_USAGE_TERMS] |
| Original format | [FORMAT, e.g. CSV export, database dump] |
| Known prior processing | [ANY_TRANSFORMATIONS_ALREADY_APPLIED_BEFORE_THIS_PIPELINE] |

## Scope

- **In scope**: [WHAT_THIS_CLEANSING_EFFORT_COVERS]
- **Out of scope**: [WHAT_IT_EXPLICITLY_DOES_NOT_COVER]

## Definition of Done

Read against `target-data-model.md`. A record is done when:

- [ ] Every field marked required in the target data model is populated or explicitly
      and legitimately left null per the constitution's ambiguity policy.
- [ ] Every populated controlled-vocabulary field uses a value from that vocabulary.
- [ ] [ADD_DATASET_SPECIFIC_DONE_CRITERIA]

The dataset as a whole is done when:

- [ ] All in-scope records meet the record-level definition of done above.
- [ ] `scripts/validate_against_model.py validate-dataset` passes with no unexplained
      failures.
- [ ] Every deviation is logged and, per the constitution, either flagged with rationale
      or resolved.

## Open Questions

Unresolved items that affect scope or the definition of done. Resolve these before
`03-plan.md` runs — do not carry ambiguity about *what* the dataset is into planning.

- [ ] [QUESTION]

## Assumptions

Reasonable defaults used to avoid open questions that don't materially change scope.

- [ASSUMPTION_AND_WHY_ITS_SAFE]
