#!/usr/bin/env python3
"""Append-only, tamper-evident changelog for dataset cleaning operations.

Every entry is one line of JSON in a JSON Lines file. Entries are chained by hash
(each entry's hash covers its own fields plus the previous entry's hash), so any edit or
reorder of prior history is detectable via `verify`. This is the mechanical backing for
the constitution's reversibility/audit principles — nothing about *what* counts as a
violation is decided here, only that every operation is durably recorded.

Usage:
    changelog.py append <log.jsonl> --dataset-id ID --operation-id CL001 \
        --description TEXT --operator NAME [--task-source PATH] \
        [--input-ref REF] [--output-ref REF] [--reversible true|false] [--notes TEXT]
    changelog.py show <log.jsonl> [--operation-id CL001]
    changelog.py verify <log.jsonl>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

GENESIS_HASH = "0" * 64


def _entry_hash(prev_hash: str, fields: dict) -> str:
    payload = json.dumps({"prev_hash": prev_hash, **fields}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _read_entries(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def cmd_append(args: argparse.Namespace) -> None:
    path = Path(args.log)
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = _read_entries(path)
    prev_hash = entries[-1]["entry_hash"] if entries else GENESIS_HASH

    fields = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_id": args.dataset_id,
        "operation_id": args.operation_id,
        "description": args.description,
        "operator": args.operator,
        "task_source": args.task_source,
        "input_ref": args.input_ref,
        "output_ref": args.output_ref,
        "reversible": args.reversible,
        "notes": args.notes,
    }
    entry = {
        "prev_hash": prev_hash,
        **fields,
        "entry_hash": _entry_hash(prev_hash, fields),
    }
    with path.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"Logged {args.operation_id} for {args.dataset_id} -> {path}")


def cmd_show(args: argparse.Namespace) -> None:
    entries = _read_entries(Path(args.log))
    if args.operation_id:
        entries = [e for e in entries if e["operation_id"] == args.operation_id]
    if not entries:
        print("No matching entries.")
        return
    for e in entries:
        print(f"{e['timestamp']}  {e['operation_id']:8s}  {e['operator']:15s}  {e['description']}")
        if e.get("input_ref") or e.get("output_ref"):
            print(f"    input: {e.get('input_ref')}  output: {e.get('output_ref')}")
        if e.get("notes"):
            print(f"    notes: {e['notes']}")


def cmd_verify(args: argparse.Namespace) -> None:
    entries = _read_entries(Path(args.log))
    prev_hash = GENESIS_HASH
    for i, e in enumerate(entries):
        fields = {k: v for k, v in e.items() if k not in ("prev_hash", "entry_hash")}
        expected = _entry_hash(prev_hash, fields)
        if e.get("prev_hash") != prev_hash or e.get("entry_hash") != expected:
            print(
                f"CORRUPT: entry {i} ({e.get('operation_id')}) does not chain from the "
                "previous entry — history has been edited or reordered.",
                file=sys.stderr,
            )
            sys.exit(1)
        prev_hash = e["entry_hash"]
    print(f"OK: {len(entries)} entries verified, chain intact.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("append")
    p.add_argument("log")
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--operation-id", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--operator", required=True)
    p.add_argument("--task-source", default=None, help="path/line in tasks.md this satisfies")
    p.add_argument("--input-ref", default=None)
    p.add_argument("--output-ref", default=None)
    p.add_argument("--reversible", choices=["true", "false"], default="true")
    p.add_argument("--notes", default=None)
    p.set_defaults(func=cmd_append)

    p = sub.add_parser("show")
    p.add_argument("log")
    p.add_argument("--operation-id", default=None)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("verify")
    p.add_argument("log")
    p.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
