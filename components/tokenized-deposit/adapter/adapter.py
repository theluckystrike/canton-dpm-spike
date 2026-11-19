"""Ledger API adapter for the tokenized deposit component.

The adapter turns a small JSON request into a Ledger API create command and
back. It has no Daml dependency, so it can be tested without a ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import json

TEMPLATE_ID = "TokenizedDeposit:DepositHolding"


@dataclass(frozen=True)
class CreateDeposit:
    issuer: str
    owner: str
    instrument: str
    amount: Decimal


def parse_create_request(payload: dict) -> CreateDeposit:
    """Read a create request and reject anything the template would reject."""
    missing = {"issuer", "owner", "instrument", "amount"} - payload.keys()
    if missing:
        raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
    amount = Decimal(str(payload["amount"]))
    if amount < 0:
        raise ValueError("amount must not be negative")
    if not str(payload["instrument"]).strip():
        raise ValueError("instrument must not be empty")
    return CreateDeposit(
        issuer=str(payload["issuer"]),
        owner=str(payload["owner"]),
        instrument=str(payload["instrument"]),
        amount=amount,
    )


def to_ledger_command(request: CreateDeposit) -> dict:
    """Build the JSON API create command body."""
    return {
        "commands": [
            {
                "CreateCommand": {
                    "templateId": TEMPLATE_ID,
                    "createArguments": {
                        "issuer": request.issuer,
                        "owner": request.owner,
                        "instrument": request.instrument,
                        "amount": str(request.amount),
                    },
                }
            }
        ]
    }


def main(path: str) -> int:
    payload = json.loads(open(path).read())
    command = to_ledger_command(parse_create_request(payload))
    print(json.dumps(command, indent=2))
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1]))
