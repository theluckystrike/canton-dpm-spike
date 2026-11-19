#!/usr/bin/env python3
"""Validate Canton DPM component index entries.

Usage:
    python tools/validate.py index/components/example-tokenized-deposit.json
    python tools/validate.py index

Exit code 0 means every entry matched index/schema.json and no two entries
share a name. Exit code 1 prints one line per problem.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "index" / "schema.json"


def collect(targets: list[str]) -> list[Path]:
    """Expand file and directory arguments into a sorted list of JSON files."""
    files: list[Path] = []
    for raw in targets:
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*.json") if p.name != "schema.json"))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(f"no such path: {raw}")
    return files


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: validate.py <file-or-directory> [...]")
        return 2

    schema = json.loads(SCHEMA_PATH.read_text())
    validator = Draft202012Validator(schema)
    problems: list[str] = []
    seen: dict[str, Path] = {}

    try:
        files = collect(argv)
    except FileNotFoundError as exc:
        print(f"FAIL {exc}")
        return 1

    if not files:
        print("FAIL no index entries found")
        return 1

    for path in files:
        try:
            entry = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            problems.append(f"{path.name}: invalid JSON ({exc.msg} at line {exc.lineno})")
            continue

        errors = sorted(validator.iter_errors(entry), key=lambda e: list(e.path))
        for error in errors:
            field = ".".join(str(p) for p in error.path) or error.validator_value
            problems.append(f"{path.name}: {field}: {error.message}")

        name = entry.get("name")
        if isinstance(name, str):
            if name in seen:
                problems.append(f"{path.name}: duplicate name '{name}' (also in {seen[name].name})")
            else:
                seen[name] = path

    if problems:
        for line in problems:
            print(f"FAIL {line}")
        return 1

    print(f"OK {len(files)} entr{'y' if len(files) == 1 else 'ies'} valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
