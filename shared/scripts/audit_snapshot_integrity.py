#!/usr/bin/env python3
"""Audit source snapshot integrity and drift behavior."""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from connectors import make_adapter
from source_snapshots import verify_snapshot_integrity

CASES = ROOT / "golden" / "snapshot_integrity_cases.json"


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    with tempfile.TemporaryDirectory(prefix="loop-kit-snapshot-") as tmp:
        root = Path(tmp)
        for case in cases:
            path = root / f"{case['id']}.txt"
            path.write_text(case["initial"])
            adapter = make_adapter("local_file")
            snapshot = adapter.freeze_source(str(path), run_dir=root / case["id"])["snapshot"]
            path.write_text(case["current"])
            current_items = adapter.collect_items(str(path))
            result = verify_snapshot_integrity(snapshot, current_items)
            expected_terminal = case["expected_terminal_state"]
            if result["terminal_state"] != expected_terminal:
                failures.append(f"{case['id']}: expected {expected_terminal}, got {result}")
            snapshot_path = root / case["id"] / "source-snapshot.json"
            if not snapshot_path.exists():
                failures.append(f"{case['id']}: source-snapshot.json missing")
            loaded = json.loads(snapshot_path.read_text())
            for field in ["adapter_name", "source_ref", "captured_at", "normalized_sha256", "item_count", "trust_level"]:
                if field not in loaded:
                    failures.append(f"{case['id']}: snapshot missing {field}")
    return {"total": len(cases), "failures": failures}


if __name__ == "__main__":
    result = run()
    print(f"audit_snapshot_integrity: {result['total'] - len(result['failures'])}/{result['total']} passed")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
