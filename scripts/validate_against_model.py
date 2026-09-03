#!/usr/bin/env python3
"""Validate project artefacts against the target data model — no schema hardcoded here.

Three modes:

  check-completeness <file.md>
      For constitution.md / target-data-model.md: fails if any [PLACEHOLDER] token or
      TODO(...)/NEEDS CLARIFICATION marker remains. 00-init.md is not done until this
      passes on both files.

  check-model <target-data-model.md>
      Parses the "## Machine-Readable Summary" YAML block and validates its shape
      (schema/fields/vocabularies keys present, every field has a name and type).

  validate-dataset <data.csv> --model <target-data-model.md>
      Loads the YAML block from --model and checks a delimited dataset against it:
      required fields present as columns, controlled-vocabulary values valid, per-field
      rules (regex) satisfied. Reports pass/fail with violation counts — makes no
      assumption about what the fields or vocabularies actually are.

Usage:
    validate_against_model.py check-completeness <file.md>
    validate_against_model.py check-model <target-data-model.md>
    validate_against_model.py validate-dataset <data.csv> --model <target-data-model.md> [--delimiter ,] [--out FILE.md|FILE.json]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import yaml

PLACEHOLDER_PATTERN = re.compile(r"\[[A-Z][A-Z0-9_ ]*\]")
TODO_PATTERN = re.compile(r"TODO\(|NEEDS CLARIFICATION")
YAML_BLOCK_PATTERN = re.compile(r"## Machine-Readable Summary\s*```yaml\n(.*?)```", re.DOTALL)


def cmd_check_completeness(args: argparse.Namespace) -> None:
    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    text = path.read_text()

    placeholders = sorted(set(PLACEHOLDER_PATTERN.findall(text)))
    todos = TODO_PATTERN.findall(text)

    if not placeholders and not todos:
        print(f"PASS: {path} has no remaining placeholders or TODO markers.")
        return

    print(f"FAIL: {path} is not complete.", file=sys.stderr)
    if placeholders:
        print(f"  Remaining placeholders ({len(placeholders)}):", file=sys.stderr)
        for p in placeholders:
            print(f"    {p}", file=sys.stderr)
    if todos:
        print(f"  Remaining TODO/NEEDS CLARIFICATION markers: {len(todos)}", file=sys.stderr)
    sys.exit(1)


def _load_model(model_path: Path) -> dict:
    text = model_path.read_text()
    match = YAML_BLOCK_PATTERN.search(text)
    if not match:
        print(
            f"ERROR: no '## Machine-Readable Summary' YAML block found in {model_path}",
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        model = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        print(f"ERROR: could not parse YAML block in {model_path}: {exc}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(model, dict):
        print(f"ERROR: YAML block in {model_path} did not parse to a mapping", file=sys.stderr)
        sys.exit(2)
    return model


def cmd_check_model(args: argparse.Namespace) -> None:
    model = _load_model(Path(args.model))
    errors = []
    for key in ("schema", "fields", "vocabularies"):
        if key not in model:
            errors.append(f"missing top-level key: {key}")

    for field in model.get("fields") or []:
        name = field.get("name")
        if not name or str(name).startswith("["):
            errors.append(f"field missing a real name: {field!r}")
            continue
        if field.get("type") not in ("string", "number", "date", "boolean", "enum"):
            errors.append(f"field '{name}' has invalid type: {field.get('type')!r}")
        vocab = field.get("vocabulary")
        if vocab and vocab not in (model.get("vocabularies") or {}):
            errors.append(f"field '{name}' references undefined vocabulary '{vocab}'")

    if errors:
        print(f"FAIL: {args.model} model block has {len(errors)} issue(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print(f"PASS: {args.model} model block is well-formed ({len(model.get('fields') or [])} fields).")


def _vocab_values(vocab_def: dict, model_path: Path) -> set[str]:
    if vocab_def.get("external_ref"):
        ref_path = (model_path.parent / vocab_def["external_ref"]).resolve()
        if not ref_path.exists():
            print(f"ERROR: vocabulary external_ref not found: {ref_path}", file=sys.stderr)
            sys.exit(2)
        return {line.strip() for line in ref_path.read_text().splitlines() if line.strip()}
    return set(vocab_def.get("values") or [])


def cmd_validate_dataset(args: argparse.Namespace) -> None:
    model_path = Path(args.model)
    model = _load_model(model_path)
    fields = {f["name"]: f for f in model.get("fields") or []}
    vocabularies = {
        name: _vocab_values(v, model_path) for name, v in (model.get("vocabularies") or {}).items()
    }

    data_path = Path(args.input)
    if not data_path.exists():
        print(f"ERROR: input file not found: {data_path}", file=sys.stderr)
        sys.exit(2)

    with data_path.open(newline="", encoding="utf-8-sig") as f:
        sample = f.read(8192)
        f.seek(0)
        delimiter = args.delimiter
        if not delimiter:
            try:
                delimiter = csv.Sniffer().sniff(sample).delimiter
            except csv.Error:
                delimiter = ","
        reader = csv.DictReader(f, delimiter=delimiter)
        columns = set(reader.fieldnames or [])

        results = {
            "missing_required_fields": [],
            "field_violations": {},
            "row_count": 0,
        }

        required_missing = [
            name for name, f in fields.items() if f.get("required") and name not in columns
        ]
        results["missing_required_fields"] = required_missing

        compiled_rules = {
            name: re.compile(f["rule"])
            for name, f in fields.items()
            if f.get("rule") and name in columns
        }

        for row in reader:
            results["row_count"] += 1
            for name, field in fields.items():
                if name not in columns:
                    continue
                value = (row.get(name) or "").strip()
                if value == "":
                    if field.get("required"):
                        results["field_violations"].setdefault(name, {"required_but_blank": 0})
                        results["field_violations"][name]["required_but_blank"] = (
                            results["field_violations"][name].get("required_but_blank", 0) + 1
                        )
                    continue
                vocab_name = field.get("vocabulary")
                if vocab_name and value not in vocabularies.get(vocab_name, set()):
                    results["field_violations"].setdefault(name, {})
                    results["field_violations"][name]["not_in_vocabulary"] = (
                        results["field_violations"][name].get("not_in_vocabulary", 0) + 1
                    )
                if name in compiled_rules and not compiled_rules[name].match(value):
                    results["field_violations"].setdefault(name, {})
                    results["field_violations"][name]["failed_rule"] = (
                        results["field_violations"][name].get("failed_rule", 0) + 1
                    )

    passed = not results["missing_required_fields"] and not results["field_violations"]
    results["status"] = "pass" if passed else "fail"

    output = json.dumps(results, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.write_text(output if out_path.suffix == ".json" else _to_markdown(results))
        print(f"Wrote validation report to {out_path}")
    else:
        print(output)

    if not passed:
        sys.exit(1)


def _to_markdown(results: dict) -> str:
    lines = [f"# Validation Report", "", f"**Status**: {results['status']}", f"**Rows**: {results['row_count']}", ""]
    if results["missing_required_fields"]:
        lines.append("## Missing required fields (no matching column)")
        for f in results["missing_required_fields"]:
            lines.append(f"- {f}")
        lines.append("")
    if results["field_violations"]:
        lines.append("## Field violations")
        lines.append("| Field | Issue | Count |")
        lines.append("|---|---|---|")
        for field, issues in results["field_violations"].items():
            for issue, count in issues.items():
                lines.append(f"| {field} | {issue} | {count} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check-completeness")
    p.add_argument("file")
    p.set_defaults(func=cmd_check_completeness)

    p = sub.add_parser("check-model")
    p.add_argument("model")
    p.set_defaults(func=cmd_check_model)

    p = sub.add_parser("validate-dataset")
    p.add_argument("input")
    p.add_argument("--model", required=True)
    p.add_argument("--delimiter", default=None)
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_validate_dataset)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
