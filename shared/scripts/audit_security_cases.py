#!/usr/bin/env python3
"""Audit prompt-injection and source-safety quarantine cases."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from source_safety import quarantine_source_text

CASE_FILES = [
    ROOT / "redteam" / "prompt_injection_cases.json",
    ROOT / "redteam" / "connector_source_cases.json",
]


def quarantine(source):
    return quarantine_source_text(source)


def run():
    cases = []
    for path in CASE_FILES:
        if path.exists():
            cases.extend(json.loads(path.read_text()))
    failures = []
    for case in cases:
        result = quarantine(case["source_text"])
        if case.get("expect_blocked") and not result["blocked"]:
            failures.append(f"{case['id']}: expected blocked")
        if case.get("expect_no_tool_action_escape") and result["tool_action"] and not result["blocked"]:
            failures.append(f"{case['id']}: tool action escaped")
        if case.get("expect_secret_quarantine") and not result["secret_leak"]:
            failures.append(f"{case['id']}: secret not detected")
        if case.get("expect_source_instruction_quarantine") and not result["source_instruction_quarantined"]:
            failures.append(f"{case['id']}: source instruction not quarantined")
        if result["secret_leak"] and any(token in json.dumps(result) for token in ["12345678abcdef", "abcd1234TOKEN", "SECRETSECRET"]):
            failures.append(f"{case['id']}: secret echoed")
        if result["blocked"] and not result["evidence_id"]:
            failures.append(f"{case['id']}: blocked case missing evidence id")
    connector_cases = [case for case in cases if str(case.get("id", "")).startswith("src-")]
    if connector_cases and len(connector_cases) < 50:
        failures.append(f"connector source-safety case count below 50: {len(connector_cases)}")
    return {"total": len(cases), "failures": failures}


if __name__ == "__main__":
    result = run()
    print(f"audit_security_cases: {result['total'] - len(result['failures'])}/{result['total']} passed")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
