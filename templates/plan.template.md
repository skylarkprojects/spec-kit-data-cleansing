# Cleaning Plan: [DATASET_NAME]

**Dataset ID**: [DATASET_ID] | **Spec**: [LINK_TO_SPEC_MD]
**Created**: [DATE]

## Field-by-Field Mapping

Every target-model field (required and optional) must appear here, even if the mapping is
"no source column — leave null."

| Target field | Source column(s) | Mapping notes | Confidence |
|---|---|---|---|
| [TARGET_FIELD] | [SOURCE_COLUMN or "none"] | [DIRECT / DERIVED / SPLIT / MERGED — describe] | [high / medium / low] |

## Transformations

One row per distinct transformation operation this dataset needs. `04-tasks.md` will turn
each of these into one or more discrete, independently verifiable tasks.

| ID | Target field(s) | Transformation | Rule source |
|---|---|---|---|
| [T1] | [FIELD(S)] | [e.g. trim whitespace, parse date format X → ISO 8601, map raw code → controlled vocabulary term] | [target-data-model rule, or dataset-specific decision] |

## Controlled Vocabulary Reconciliation

For every field that maps to a controlled vocabulary in `target-data-model.md`, how raw
values will be reconciled to it.

| Field | Raw value pattern | Vocabulary | Reconciliation approach | Unmatched-value handling |
|---|---|---|---|---|
| [FIELD] | [PATTERN_OR_EXAMPLES] | [VOCAB_NAME] | [exact match / lookup table / fuzzy match + review] | [per constitution escalation rule] |

## Gaps & Risks

Everything that keeps this dataset from cleanly meeting the target model, and what happens
per the constitution's flag-vs-block rule.

| Gap / risk | Affected field(s) | Severity | Flag or block? | Mitigation |
|---|---|---|---|---|
| [DESCRIPTION] | [FIELD(S)] | [low/med/high] | [flag/block] | [WHAT_WILL_BE_DONE] |

## Out-of-Model Data

Source columns that don't map to anything in the target data model.

| Source column | Disposition |
|---|---|
| [COLUMN] | [drop / retain as extension field / retain in a side artifact — justify] |

## Validation Strategy

How `05-implement.md` will confirm the plan was executed correctly.

- [ ] `scripts/validate_against_model.py validate-dataset` against every required field
      and vocabulary above.
- [ ] [ADD_DATASET_SPECIFIC_VALIDATION_STEPS, e.g. row-count reconciliation against the
      audit report, spot-check sample size]
