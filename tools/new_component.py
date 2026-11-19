#!/usr/bin/env python3
"""Generate a minimal DPM component scaffold.

    python tools/new_component.py cash-leg --kind template-plugin

The generator writes four files that a reviewer can read in a few minutes and
that already pass tools/validate.py. It refuses names that are not kebab-case,
because the index schema does.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KINDS = ["template-plugin", "scaffold", "ledger-api-adapter", "ui-block"]

DAML_TEMPLATE = """module {module} where

-- Scaffolded by tools/new_component.py. Compile with `daml build`.

template {module}
  with
    issuer : Party
    owner : Party
  where
    signatory issuer, owner

    choice ArchiveHolding : ()
      controller owner
      do pure ()
"""

ADAPTER_TEMPLATE = '''"""Adapter for the {name} component. No Daml dependency, so it tests without a ledger."""

from __future__ import annotations

import json

TEMPLATE_ID = "{module}:{module}"


def to_create_command(issuer: str, owner: str) -> dict:
    """Build a Ledger API create command for one holding."""
    return {{
        "commands": [
            {{
                "CreateCommand": {{
                    "templateId": TEMPLATE_ID,
                    "createArguments": {{"issuer": issuer, "owner": owner}},
                }}
            }}
        ]
    }}


def main(path: str) -> int:
    payload = json.loads(open(path).read())
    print(json.dumps(to_create_command(payload["issuer"], payload["owner"]), indent=2))
    return 0
'''

README_TEMPLATE = """# {name}

Scaffolded DPM component of kind `{kind}`.

| Path | Purpose |
| --- | --- |
| `daml/{module}.daml` | Template with one archive choice |
| `adapter/adapter.py` | JSON to Ledger API create command |
| `index.json` | Index entry for `index/components/` |

## Next steps

1. Replace the template body with real business logic.
2. Run `daml build` in `daml/` once the SDK is installed.
3. Copy `index.json` into `index/components/` and run `python tools/validate.py index`.
"""


def git_value(key: str, fallback: str) -> str:
    """Read one git config value, with a fallback for empty repos."""
    try:
        out = subprocess.run(
            ["git", "config", "--get", key], capture_output=True, text=True, check=False
        ).stdout.strip()
    except OSError:
        return fallback
    return out or fallback


def pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("-"))


def build_files(name: str, kind: str, maintainer: str, url: str) -> dict[str, str]:
    module = pascal(name)
    entry = {
        "name": name,
        "display_name": name.replace("-", " ").title(),
        "version": "0.1.0",
        "component_kind": kind,
        "daml_sdk_version": "3.4.0",
        "entry_point": f"./{name}/",
        "integrity": {"sha256": "0" * 64},
        "license": "Apache-2.0",
        "capabilities": [f"scaffold {kind} component"],
        "permissions": ["ledger-read"],
        "maintainer": {"name": maintainer, "url": url},
        "description": f"Scaffolded {kind} component for Canton DPM, generated for {name}.",
    }
    body = json.dumps(entry, indent=2) + "\n"
    entry["integrity"]["sha256"] = hashlib.sha256(body.encode()).hexdigest()

    return {
        f"daml/{module}.daml": DAML_TEMPLATE.format(module=module),
        "adapter/adapter.py": ADAPTER_TEMPLATE.format(name=name, module=module),
        "index.json": json.dumps(entry, indent=2) + "\n",
        "README.md": README_TEMPLATE.format(name=name, kind=kind, module=module),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate a minimal DPM component scaffold.")
    parser.add_argument("name", help="component name in kebab-case")
    parser.add_argument("--kind", default="template-plugin", choices=KINDS)
    parser.add_argument("--out", default=".", help="directory to create the component in")
    parser.add_argument("--maintainer", default=git_value("user.name", "Component Author"))
    parser.add_argument("--maintainer-url", default="https://github.com/")
    args = parser.parse_args(argv)

    if not KEBAB.match(args.name):
        print(f"error: name must be kebab-case, for example cash-leg (got '{args.name}')", file=sys.stderr)
        return 2

    base = Path(args.out) / args.name
    if base.exists():
        print(f"error: {base} already exists", file=sys.stderr)
        return 1

    for rel, content in build_files(args.name, args.kind, args.maintainer, args.maintainer_url).items():
        target = base / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    print(f"created {base} ({len(build_files(args.name, args.kind, args.maintainer, args.maintainer_url))} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
