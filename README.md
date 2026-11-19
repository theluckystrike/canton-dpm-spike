# Canton DPM component index

A small, readable answer to a big question: what does a DPM component look like
when it ships as data plus a scaffold, instead of a proposal?

This repository supports the RFP 19 submission. It is a working spike, not a
product. Every file here is short enough to read in one sitting.

## What is here

- `index/schema.json`: JSON Schema for one index entry, draft 2020-12
- `index/components/`: validated entries, one example included
- `components/tokenized-deposit/`: complete reference component with Daml template, adapter and example request
- `tools/validate.py`: checks entries against the schema and rejects duplicate names
- `tools/new_component.py`: generates a component scaffold that already validates

The `tests/` directory holds 13 tests covering the validator, the adapter and the generator.

## Try it

    python -m pytest tests -q
    python tools/validate.py index
    python tools/new_component.py cash-leg

Each command needs only `jsonschema` and `pytest`.

## Design choices

An entry names an OCI artifact with an explicit tag and a sha256, so install is
pinned and verifiable. Permissions are a closed list, so a component cannot ask
for a capability the platform does not have. Two entries cannot share a name, so
the index stays a set and not a list of near-duplicates.

The Daml package is not built in CI, because the runner has no SDK. That gap is
stated in the component README rather than hidden.

## Relation to RFP 19

The DPM use-case list published by the Foundation names "Custom Daml Template
Plugin" first, under Project Scaffolding. This repository is one concrete
instance of that pattern: a template, a frontend stub and a generator, with a
validation contract that a maintainer can enforce in CI.

## License

Apache-2.0. See `LICENSE`.
