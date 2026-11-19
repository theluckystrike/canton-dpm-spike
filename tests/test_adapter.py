"""Tests for the tokenized deposit adapter."""

from decimal import Decimal
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "components" / "tokenized-deposit" / "adapter"))

import adapter  # noqa: E402

EXAMPLE = Path(__file__).resolve().parents[1] / "components" / "tokenized-deposit" / "examples" / "create-deposit.json"


def test_example_request_parses():
    request = adapter.parse_create_request(json.loads(EXAMPLE.read_text()))
    assert request.amount == Decimal("1000.00")
    assert request.instrument == "USD-CASH"


def test_command_shape():
    request = adapter.parse_create_request(json.loads(EXAMPLE.read_text()))
    command = adapter.to_ledger_command(request)
    create = command["commands"][0]["CreateCommand"]
    assert create["templateId"] == "TokenizedDeposit:DepositHolding"
    assert create["createArguments"]["amount"] == "1000.00"


def test_negative_amount_is_rejected():
    payload = {"issuer": "I", "owner": "O", "instrument": "USD", "amount": "-1"}
    try:
        adapter.parse_create_request(payload)
    except ValueError as exc:
        assert "negative" in str(exc)
    else:
        raise AssertionError("negative amount accepted")


def test_missing_field_is_rejected():
    payload = {"issuer": "I", "owner": "O", "amount": "1"}
    try:
        adapter.parse_create_request(payload)
    except ValueError as exc:
        assert "instrument" in str(exc)
    else:
        raise AssertionError("missing field accepted")
