#!/usr/bin/env python3
"""Audit V3-B schedule-readiness proposal artifacts."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from graduation import evaluate_graduation
from schedule_proposals import render_schedule_proposal, validate_schedule_proposal

CASES = ROOT / "golden" / "schedule_proposal_cases.json"


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    now = datetime(2026, 6, 24, 12, 0, 0, tzinfo=timezone.utc)
    for case in cases:
        evaluation = evaluate_graduation(case["profile"], case.get("acceptance_records", []), case.get("cost_records", []))
        proposal = render_schedule_proposal(evaluation, case["profile"], now=now)
        proposal.update(case.get("mutate_proposal", {}))
        result = validate_schedule_proposal(proposal, evaluation=evaluation, now=now)
        expected = bool(case["expected_valid"])
        if result["valid"] != expected:
            failures.append(f"{case['id']}: expected valid={expected}, got {result}")
        expected_failure = case.get("expected_failure_contains")
        if expected_failure and expected_failure not in result["failures"]:
            failures.append(f"{case['id']}: missing failure {expected_failure!r}, got {result['failures']}")
    return {"total": len(cases), "failures": failures}


if __name__ == "__main__":
    result = run()
    print(f"audit_schedule_proposals: {result['total'] - len(result['failures'])}/{result['total']} passed")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
