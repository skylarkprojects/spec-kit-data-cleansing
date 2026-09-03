<!--
This file has two parts:
1. Human-readable sections below, for authors and reviewers.
2. A machine-readable YAML block at the bottom (`## Machine-Readable Summary`), which
   `scripts/validate_against_model.py` and `scripts/profile_dataset.py` parse directly.
Keep both in sync — the YAML block is the source of truth the scripts enforce; the prose
above it is what `00-init.md` interviews the user to produce.
-->

# [PROJECT_NAME] Target Data Model

## Target Schema / Standard

- **Name**: [TARGET_SCHEMA_NAME — the standard or internal schema every cleaned dataset
  must align to]
- **Version**: [TARGET_SCHEMA_VERSION]
- **Authoritative source**: [LINK_OR_CITATION_TO_THE_STANDARD]
- **Scope note**: [DESCRIBE_WHAT_PART_OF_THE_STANDARD_APPLIES, if only a subset is in
  scope for this project]

## Required Fields

Fields every cleaned dataset MUST populate before a record is considered done. Leave a
field null only when Principle III (Handling of Ambiguous or Uncertain Values) in the
constitution explicitly allows it.

| Field | Type | Description | Required by standard or by this project? |
|---|---|---|---|
| [FIELD_NAME] | [string/number/date/boolean/enum] | [WHAT_IT_MEANS] | [standard/project] |

## Optional Fields

Fields the target model accepts but does not require.

| Field | Type | Description | When it should be populated |
|---|---|---|---|
| [FIELD_NAME] | [TYPE] | [WHAT_IT_MEANS] | [CONDITION] |

## Controlled Vocabularies / Reference Lists

For each field whose values must come from a fixed list.

| Vocabulary name | Applies to field(s) | Source | How it's kept current |
|---|---|---|---|
| [VOCAB_NAME] | [FIELD_NAME] | [SOURCE_URL_OR_FILE] | [UPDATE_CADENCE_OR_PROCESS] |

## Field-Level Validation Rules

Rules beyond "required" / "controlled vocabulary" — format constraints, ranges,
cross-field consistency checks.

| Field | Rule | Failure handling |
|---|---|---|
| [FIELD_NAME] | [e.g. regex, numeric range, date format, must-be-unique] | [flag / block — reference the constitution's escalation rule] |

## Known Extensions & Deviations from the Base Standard

- [DESCRIBE_ANY_PROJECT_SPECIFIC_FIELD_NOT_IN_THE_BASE_STANDARD, and why it was added]
- [DESCRIBE_ANY_BASE_STANDARD_FIELD_THIS_PROJECT_DELIBERATELY_IGNORES, and why]

## Machine-Readable Summary

`scripts/validate_against_model.py` reads this block directly — keep every field listed
above mirrored here. `check-completeness` fails if this block is missing, unparsable, or
still contains the placeholder example.

```yaml
schema:
  name: "[TARGET_SCHEMA_NAME]"
  version: "[TARGET_SCHEMA_VERSION]"
  source: "[LINK_OR_CITATION]"
fields:
  - name: "[FIELD_NAME]"
    required: true
    type: string   # string | number | date | boolean | enum
    vocabulary: null   # name of a vocabulary below, or null
    rule: null         # regex or short rule description, or null
    notes: ""
vocabularies:
  "[VOCAB_NAME]":
    source: "[SOURCE_URL_OR_FILE]"
    values: []          # inline list, or:
    external_ref: null  # path/URL to load values from instead
```
