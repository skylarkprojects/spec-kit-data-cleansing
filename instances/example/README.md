# Example Instance (stub)

This directory is intentionally empty of real content — it exists only to show the shape
an instance takes once `prompts/00-init.md` has been run, so a new instance's directory
listing has something to compare against.

A real, filled-in instance would have:

```text
instances/example/
  constitution.md          # no [PLACEHOLDER] tokens remaining
  target-data-model.md     # no [PLACEHOLDER] tokens remaining, YAML block populated
  registry/
    widgets-2026-export.yaml
  datasets/
    widgets-2026-export/
      audit-report.md
      spec.md
      plan.md
      tasks.md
      changelog.jsonl
      validation-report.md
```

This package contains no such content for `example/` — no target schema, no field lists,
no vocabularies. Populating it means running `prompts/00-init.md` against a real project's
target data model, not copying an existing domain's answers here. Any project-specific
instance (including one built from a prior fork of this methodology) belongs in its own
instance directory, never merged into this stub.
