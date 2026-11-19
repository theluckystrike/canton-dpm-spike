"""Tests for the component scaffold generator."""

from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run_scaffold(tmp_path, *args):
    cmd = [sys.executable, str(ROOT / "tools" / "new_component.py"), *args]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=tmp_path)


def test_scaffold_writes_expected_tree(tmp_path):
    proc = run_scaffold(tmp_path, "cash-leg", "--kind", "template-plugin")
    assert proc.returncode == 0, proc.stderr
    base = tmp_path / "cash-leg"
    for rel in ["daml/CashLeg.daml", "adapter/adapter.py", "index.json", "README.md"]:
        assert (base / rel).is_file(), rel
    entry = json.loads((base / "index.json").read_text())
    assert entry["name"] == "cash-leg"
    assert entry["component_kind"] == "template-plugin"


def test_scaffold_refuses_bad_name(tmp_path):
    proc = run_scaffold(tmp_path, "Cash Leg")
    assert proc.returncode == 2
    assert "kebab" in proc.stderr.lower()


def test_scaffolded_entry_passes_validator(tmp_path):
    assert run_scaffold(tmp_path, "cash-leg").returncode == 0
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate.py"), str(tmp_path / "cash-leg" / "index.json")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout
