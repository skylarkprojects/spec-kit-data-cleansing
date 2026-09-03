#!/usr/bin/env python3
"""Stage-gate enforcement for the data cleansing pipeline.

Reads and writes dataset registry entries (registry/schema.yaml) so that a prompt phase
can only proceed once the artefact required before it exists AND is marked approved —
never on a bare file-exists check.

Usage:
    stage_gate.py init-dataset <entry.yaml> --dataset-id ID --name NAME --source SRC \
        --owner OWNER --raw-path PATH --changelog-path PATH
    stage_gate.py check <entry.yaml> --stage {audit,specify,plan,tasks,implement}
    stage_gate.py set-artifact <entry.yaml> --stage STAGE --path PATH
    stage_gate.py approve <entry.yaml> --stage STAGE --by NAME [--notes TEXT]
    stage_gate.py reject <entry.yaml> --stage STAGE --by NAME --notes TEXT
    stage_gate.py status <entry.yaml>
"""
from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

import yaml

STAGES = ["audit", "specify", "plan", "tasks", "implement"]


def _today() -> str:
    return datetime.date.today().isoformat()


def _empty_stage() -> dict:
    return {
        "status": "draft",
        "artifact_path": None,
        "approved_by": None,
        "approved_date": None,
        "notes": None,
    }


def load_entry(path: Path) -> dict:
    if not path.exists():
        print(f"ERROR: registry entry not found: {path}", file=sys.stderr)
        sys.exit(2)
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("stages", {})
    for stage in STAGES:
        data["stages"].setdefault(stage, _empty_stage())
    return data


def save_entry(path: Path, data: dict) -> None:
    with path.open("w") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)


def cmd_init_dataset(args: argparse.Namespace) -> None:
    path = Path(args.entry)
    if path.exists():
        print(f"ERROR: registry entry already exists: {path}", file=sys.stderr)
        sys.exit(2)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "dataset_id": args.dataset_id,
        "name": args.name,
        "source": args.source,
        "owner": args.owner,
        "added_date": _today(),
        "raw_path": args.raw_path,
        "changelog_path": args.changelog_path,
        "stages": {stage: _empty_stage() for stage in STAGES},
    }
    save_entry(path, data)
    print(f"Created registry entry: {path}")


def cmd_check(args: argparse.Namespace) -> None:
    data = load_entry(Path(args.entry))
    stage = args.stage
    idx = STAGES.index(stage)
    if idx == 0:
        print(
            f"OK: '{stage}' has no prior-stage gate; run 00-init.md's completeness "
            "check on constitution.md and target-data-model.md instead."
        )
        return
    prior = STAGES[idx - 1]
    prior_status = data["stages"][prior]["status"]
    if prior_status == "approved":
        print(f"OK: '{prior}' is approved — '{stage}' may proceed.")
        return
    print(
        f"BLOCKED: '{stage}' requires '{prior}' to be approved "
        f"(currently: {prior_status}).",
        file=sys.stderr,
    )
    sys.exit(1)


def cmd_set_artifact(args: argparse.Namespace) -> None:
    path = Path(args.entry)
    data = load_entry(path)
    data["stages"][args.stage]["artifact_path"] = args.path
    save_entry(path, data)
    print(f"Set {args.stage}.artifact_path = {args.path}")


def _set_status(args: argparse.Namespace, status: str) -> None:
    path = Path(args.entry)
    data = load_entry(path)
    stage_data = data["stages"][args.stage]
    if status == "approved" and not stage_data.get("artifact_path"):
        print(
            f"ERROR: cannot approve '{args.stage}' — no artifact_path recorded yet.",
            file=sys.stderr,
        )
        sys.exit(2)
    stage_data["status"] = status
    stage_data["approved_by"] = args.by
    stage_data["approved_date"] = _today()
    if args.notes:
        stage_data["notes"] = args.notes
    save_entry(path, data)
    print(f"{args.stage}: status -> {status} (by {args.by})")


def cmd_approve(args: argparse.Namespace) -> None:
    _set_status(args, "approved")


def cmd_reject(args: argparse.Namespace) -> None:
    if not args.notes:
        print("ERROR: --notes is required when rejecting a stage.", file=sys.stderr)
        sys.exit(2)
    _set_status(args, "rejected")


def cmd_status(args: argparse.Namespace) -> None:
    data = load_entry(Path(args.entry))
    print(f"Dataset: {data.get('dataset_id')} ({data.get('name')})")
    for stage in STAGES:
        s = data["stages"][stage]
        marker = {"approved": "✓", "rejected": "✗", "draft": "-"}.get(
            s["status"], "?"
        )
        print(f"  [{marker}] {stage:10s} {s['status']:9s} {s.get('artifact_path') or ''}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init-dataset")
    p.add_argument("entry")
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--raw-path", required=True)
    p.add_argument("--changelog-path", required=True)
    p.set_defaults(func=cmd_init_dataset)

    p = sub.add_parser("check")
    p.add_argument("entry")
    p.add_argument("--stage", required=True, choices=STAGES)
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("set-artifact")
    p.add_argument("entry")
    p.add_argument("--stage", required=True, choices=STAGES)
    p.add_argument("--path", required=True)
    p.set_defaults(func=cmd_set_artifact)

    p = sub.add_parser("approve")
    p.add_argument("entry")
    p.add_argument("--stage", required=True, choices=STAGES)
    p.add_argument("--by", required=True)
    p.add_argument("--notes")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("reject")
    p.add_argument("entry")
    p.add_argument("--stage", required=True, choices=STAGES)
    p.add_argument("--by", required=True)
    p.add_argument("--notes", required=True)
    p.set_defaults(func=cmd_reject)

    p = sub.add_parser("status")
    p.add_argument("entry")
    p.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
