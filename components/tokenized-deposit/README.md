# Tokenized deposit component

A reference component for the Canton DPM index. It shows the smallest complete
unit that a team can copy: one Daml template, one adapter, one example request.

## Install

The index entry points at an OCI artifact with an explicit tag:

    oci://ghcr.io/theluckystrike/dpm-tokenized-deposit:0.1.0

Pin the tag and check `integrity.sha256` before use. The artifact carries no
network access and asks for two permissions: `ledger-read` and `ledger-write`.

## Files

- `daml/TokenizedDeposit.daml`: holding template with one transfer choice
- `adapter/adapter.py`: JSON request to Ledger API create command
- `examples/create-deposit.json`: input for the adapter

## Run the adapter locally

    python components/tokenized-deposit/adapter/adapter.py \
      components/tokenized-deposit/examples/create-deposit.json

The command prints a `CreateCommand` body. Nothing is sent to a ledger.

## Build the Daml package

    cd components/tokenized-deposit/daml && daml build

The Daml package is not compiled in CI, because the SDK is not installed on
the runner. CI checks the index entry and the adapter tests only.
