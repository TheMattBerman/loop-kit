#!/usr/bin/env python3
"""Audit V3-B graduation scoring cases."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from graduation import evaluate_graduation

CASES = ROOT / "golden" / "graduation_cases.json"


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    false_graduations = 0
    for case in cases:
        result = evaluate_graduation(case["profile"], case.get("acceptance_records", []), case.get("cost_records", []))
        expected = bool(case["expected_eligible"])
        if result["eligible"] != expected:
            failures.append(f"{case['id']}: expected eligible={expected}, got {result}")
        if not expected and result["eligible"]:
            false_graduations += 1
        expected_failure = case.get("expected_failure_contains")
        if expected_failure and expected_failure not in result["failures"]:
            failures.append(f"{case['id']}: missing failure {expected_failure!r}, got {result['failures']}")
    if len(cases) < 10:
        failures.append(f"graduation case count below 10: {len(cases)}")
    if false_graduations:
        failures.append(f"false graduations: {false_graduations}")
    return {"total": len(cases), "failures": failures}


if __name__ == "__main__":
    result = run()
    print(f"audit_graduation_cases: {result['total'] - len(result['failures'])}/{result['total']} passed")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
