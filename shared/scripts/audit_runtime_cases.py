#!/usr/bin/env python3
"""Run runtime/checkpoint golden cases."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from review_gate import validate_review_packet
from runtime_policy import evaluate_close
from spec_schema import validate_spec


CASES = ROOT / "golden" / "runtime_cases.json"


def run_case(case):
    kind = case["kind"]
    if kind == "spec":
        result = validate_spec(case["spec"])
        passed = result["valid"] == case["expect_pass"]
        return passed, result
    if kind == "runtime_close":
        result = evaluate_close(**case["input"])
        passed = result["allowed"] == case["expect_pass"]
        if case.get("must_not_emit"):
            passed = passed and all(result.get("schedule_recommendation") != value for value in case["must_not_emit"])
        return passed, result
    if kind == "review_gate":
        result = validate_review_packet(case["packet"])
        return result["passed"] == case["expect_pass"], result
    raise ValueError(f"unknown case kind:{kind}")


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    for case in cases:
        passed, result = run_case(case)
        if not passed:
            failures.append(f"{case['id']}: {result}")
    return {"passed": len(cases) - len(failures), "failed": len(failures), "failures": failures}


if __name__ == "__main__":
    result = run()
    total = result["passed"] + result["failed"]
    print(f"audit_runtime_cases: {result['passed']}/{total} passed")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failed"] else 0)
