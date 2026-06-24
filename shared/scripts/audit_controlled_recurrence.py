#!/usr/bin/env python3
"""Audit V4 sandbox controlled recurrence cases."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from controlled_recurrence import run_sandbox_recurrence, summarize_controlled_runs

CASES = ROOT / "golden" / "controlled_recurrence_cases.json"


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    results = []
    for case in cases:
        result = run_sandbox_recurrence(case["proposal"], case["runs"], expected_runtime_seconds=20)
        results.append(result)
        if result["creates_schedule"]:
            failures.append(f"{case['id']}: created a real schedule")
        if not result["proposal_valid"]:
            failures.append(f"{case['id']}: invalid proposal {result['proposal_failures']}")
        if result["final_status"] != case["expected_final_status"]:
            failures.append(f"{case['id']}: expected {case['expected_final_status']}, got {result['final_status']}")
        expected_pause = case.get("expected_pause_contains")
        if expected_pause:
            reasons = [reason for item in result["ledger"] for reason in item.get("pause_reasons", [])]
            if expected_pause not in reasons:
                failures.append(f"{case['id']}: missing pause reason {expected_pause!r}, got {reasons}")
        if any(not item.get("evidence_ids") for item in result["ledger"]):
            failures.append(f"{case['id']}: missing evidence in ledger")
    summary = summarize_controlled_runs(results)
    if len(cases) < 5:
        failures.append(f"controlled recurrence case count below 5: {len(cases)}")
    if summary["total_runs"] < 20:
        failures.append(f"controlled recurrence run count below 20: {summary['total_runs']}")
    if summary["valid_close_rate"] < 0.9:
        failures.append(f"valid close rate below 90%: {summary['valid_close_rate']}")
    if summary["silent_failures"]:
        failures.append(f"silent failures: {summary['silent_failures']}")
    if summary["creates_schedule"]:
        failures.append("audit created a real schedule")
    return {"total": len(cases), "runs": summary["total_runs"], "failures": failures}


if __name__ == "__main__":
    result = run()
    print(f"audit_controlled_recurrence: {result['total'] - len(result['failures'])}/{result['total']} cases passed; runs={result['runs']}")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
