# Dataset Registry

Every dataset moving through the spec-driven data cleansing pipeline gets exactly one
registry entry: a YAML file conforming to [`schema.yaml`](schema.yaml).

## Where entries live

Registry entries are project data, not package data — they live in the instance, not
here:

```text
instances/<name>/registry/<dataset_id>.yaml
```

This directory only holds the schema definition that every entry must conform to.

## Why a registry entry, not just a file-exists check

The methodology's stage gate (`scripts/stage_gate.py`) needs to distinguish "the artifact
exists" from "the artifact was approved." A prompt could produce a plausible-looking
`spec.md` that no one has reviewed — if `03-plan.md` only checked for the file's
existence, it would happily plan against unreviewed scope. The registry entry's
`stages.<stage>.status` field makes approval an explicit, recorded act (`draft` →
`approved` or `rejected`), separate from the artifact's existence.

## Lifecycle

1. `01-audit.md` creates the entry (`scripts/stage_gate.py init-dataset`) with every stage
   at `status: draft`.
2. Each prompt (`01-audit.md` … `05-implement.md`) writes its artifact and sets that
   stage's `artifact_path`, leaving `status: draft`.
3. A human reviewer runs `scripts/stage_gate.py approve <entry> --stage <stage> --by
   <name>` (or `set-status ... --status rejected` to send it back).
4. The next prompt's precondition check
   (`scripts/stage_gate.py check <entry> --stage <next-stage>`) only succeeds once the
   prior stage is `approved`.

See `docs/methodology-overview.md` for how this fits into the six artifacts overall.
