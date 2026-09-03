#!/usr/bin/env python3
"""Generic, domain-agnostic dataset profiler for the audit stage.

Reads a delimited text file and reports column inventory, null rates, detected value
formats, and cardinality — nothing schema- or vocabulary-aware. `01-audit.md` uses this
output as raw material for the audit report; it never decides what anything *means*.

Usage:
    profile_dataset.py <input.csv> [--delimiter ,] [--sample-values 5] [--out FILE.md|FILE.json]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

FORMAT_PATTERNS = [
    ("iso_date", re.compile(r"^\d{4}-\d{2}-\d{2}$")),
    ("iso_datetime", re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")),
    ("integer", re.compile(r"^-?\d+$")),
    ("decimal", re.compile(r"^-?\d+\.\d+$")),
    ("boolean_like", re.compile(r"^(true|false|yes|no|y|n|0|1)$", re.IGNORECASE)),
    ("email_like", re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")),
    ("url_like", re.compile(r"^https?://", re.IGNORECASE)),
]


def sniff_delimiter(sample: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    try:
        return csv.Sniffer().sniff(sample).delimiter
    except csv.Error:
        return ","


def detect_format(value: str) -> str | None:
    for name, pattern in FORMAT_PATTERNS:
        if pattern.match(value):
            return name
    return None


def profile_file(path: Path, delimiter: str | None, sample_values: int) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as f:
        sample = f.read(8192)
        f.seek(0)
        delim = sniff_delimiter(sample, delimiter)
        reader = csv.DictReader(f, delimiter=delim)
        fieldnames = reader.fieldnames or []
        columns = {
            name: {
                "non_null": 0,
                "blank": 0,
                "total": 0,
                "distinct": Counter(),
                "formats": Counter(),
                "max_len": 0,
                "min_len": None,
            }
            for name in fieldnames
        }
        row_count = 0
        for row in reader:
            row_count += 1
            for name in fieldnames:
                value = (row.get(name) or "").strip()
                col = columns[name]
                col["total"] += 1
                if value == "":
                    col["blank"] += 1
                    continue
                col["non_null"] += 1
                col["distinct"][value] += 1
                col["max_len"] = max(col["max_len"], len(value))
                col["min_len"] = value.__len__() if col["min_len"] is None else min(col["min_len"], len(value))
                fmt = detect_format(value)
                if fmt:
                    col["formats"][fmt] += 1

    report = {
        "file": str(path),
        "delimiter": delim,
        "row_count": row_count,
        "column_count": len(fieldnames),
        "columns": [],
    }
    for name in fieldnames:
        col = columns[name]
        distinct_count = len(col["distinct"])
        report["columns"].append(
            {
                "name": name,
                "null_rate": round(col["blank"] / col["total"], 4) if col["total"] else None,
                "distinct_count": distinct_count,
                "likely_unique_key": row_count > 0 and distinct_count == col["non_null"] == row_count,
                "min_len": col["min_len"],
                "max_len": col["max_len"],
                "detected_formats": dict(col["formats"].most_common()),
                "sample_values": [v for v, _ in col["distinct"].most_common(sample_values)],
            }
        )
    return report


def to_markdown(report: dict) -> str:
    lines = [
        f"# Profile: {report['file']}",
        "",
        f"- Delimiter: `{report['delimiter']}`",
        f"- Rows: {report['row_count']}",
        f"- Columns: {report['column_count']}",
        "",
        "| Column | Null rate | Distinct | Likely key | Detected formats | Sample values |",
        "|---|---|---|---|---|---|",
    ]
    for col in report["columns"]:
        formats = ", ".join(col["detected_formats"]) or "-"
        samples = ", ".join(repr(v) for v in col["sample_values"]) or "-"
        key = "yes" if col["likely_unique_key"] else ""
        lines.append(
            f"| {col['name']} | {col['null_rate']} | {col['distinct_count']} | {key} "
            f"| {formats} | {samples} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--delimiter", default=None)
    parser.add_argument("--sample-values", type=int, default=5)
    parser.add_argument("--out", default=None, help="write report here (.md or .json); default: stdout markdown")
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"ERROR: input file not found: {path}", file=sys.stderr)
        sys.exit(2)

    report = profile_file(path, args.delimiter, args.sample_values)

    if args.out:
        out_path = Path(args.out)
        if out_path.suffix == ".json":
            out_path.write_text(json.dumps(report, indent=2))
        else:
            out_path.write_text(to_markdown(report))
        print(f"Wrote profile to {out_path}")
    else:
        print(to_markdown(report))


if __name__ == "__main__":
    main()
