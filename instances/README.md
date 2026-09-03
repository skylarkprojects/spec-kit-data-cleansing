# Instances

This is where filled-in projects live — **not** part of the methodology package itself.
Nothing in `/templates`, `/prompts`, or `/scripts` may reference anything under here by
name; the relationship only ever runs the other way (an instance reads the templates and
runs the prompts/scripts against its own data).

## What goes in an instance

```text
instances/<name>/
  constitution.md          # filled in from templates/constitution.template.md
  target-data-model.md     # filled in from templates/target-data-model.template.md
  registry/
    <dataset_id>.yaml       # one per dataset, conforms to registry/schema.yaml
  datasets/
    <dataset_id>/
      audit-report.md
      spec.md
      plan.md
      tasks.md
      changelog.jsonl
      validation-report.md
```

## How an instance gets created

Run `prompts/00-init.md`. It interviews you to fill in `constitution.md` and
`target-data-model.md` for your specific project and target schema, and won't consider
initialisation complete until both pass `scripts/validate_against_model.py
check-completeness`. Only after that does `prompts/01-audit.md` accept a raw dataset.

See [`example/README.md`](example/README.md) for a stub showing the expected shape of a
started-but-not-filled-in instance, and `docs/methodology-overview.md` for how the six
artefacts relate.
