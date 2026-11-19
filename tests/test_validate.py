"""Tests for the component index validator.

The suite is written before the validator exists. Run it now and it fails,
which is the point: the checks below define the contract first.
"""

from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VALID_ENTRY = ROOT / "index" / "components" / "example-tokenized-deposit.json"


def run_validator(*paths):
    """Run tools/validate.py and return (exit_code, stdout)."""
    cmd = [sys.executable, str(ROOT / "tools" / "validate.py"), *map(str, paths)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def write_entry(tmp_path, name, **overrides):
    """Write a copy of the golden entry with fields overridden."""
    entry = json.loads(VALID_ENTRY.read_text())
    entry.update(overrides)
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(entry, indent=2))
    return path


def test_golden_entry_is_valid():
    code, out = run_validator(VALID_ENTRY)
    assert code == 0, out
    assert "OK" in out


def test_missing_license_is_rejected(tmp_path):
    path = write_entry(tmp_path, "no-license")
    entry = json.loads(path.read_text())
    del entry["license"]
    path.write_text(json.dumps(entry))
    code, out = run_validator(path)
    assert code == 1, out
    assert "license" in out


def test_bad_sha256_is_rejected(tmp_path):
    path = write_entry(tmp_path, "bad-hash", integrity={"sha256": "abc123"})
    code, out = run_validator(path)
    assert code == 1, out
    assert "sha256" in out


def test_malformed_oci_reference_is_rejected(tmp_path):
    path = write_entry(tmp_path, "bad-oci", entry_point="oci://registry.example.com/no-tag")
    code, out = run_validator(path)
    assert code == 1, out
    assert "entry_point" in out


def test_duplicate_names_are_rejected(tmp_path):
    first = write_entry(tmp_path, "dup-a")
    second = write_entry(tmp_path, "dup-b")
    code, out = run_validator(first, second)
    assert code == 1, out
    assert "duplicate" in out.lower()


def test_whole_index_directory_passes():
    code, out = run_validator(ROOT / "index")
    assert code == 0, out
