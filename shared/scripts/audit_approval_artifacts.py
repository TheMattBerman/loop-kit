#!/usr/bin/env python3
"""Audit approval artifact fraud cases."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from approval_artifacts import validate_approval_artifact

CASES = ROOT / "golden" / "approval_artifact_cases.json"


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    false_approvals = 0
    now = datetime(2026, 6, 24, 12, 0, 0, tzinfo=timezone.utc)
    for case in cases:
        result = validate_approval_artifact(
            case.get("artifact"),
            case["action_plan"],
            used_approvals=case.get("used_approvals", []),
            now=now,
        )
        expected = case["expected"] == "approved"
        if result["approved"] != expected:
            failures.append(f"{case['id']}: expected {case['expected']}, got {result}")
        if case["expected"] == "blocked" and result["approved"]:
            false_approvals += 1
    if len(cases) < 20:
        failures.append(f"approval artifact case count below 20: {len(cases)}")
    if false_approvals:
        failures.append(f"false approvals: {false_approvals}")
    return {"total": len(cases), "failures": failures}


if __name__ == "__main__":
    result = run()
    print(f"audit_approval_artifacts: {result['total'] - len(result['failures'])}/{result['total']} passed")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
