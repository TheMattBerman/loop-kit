#!/usr/bin/env python3
"""Audit advanced loop-improvement cases."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "shared" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import loop_diagnose

CASES = ROOT / "golden" / "advanced_improvement_cases.json"


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    intended = 0
    replacements = 0
    verifier_or_review = 0
    for case in cases:
        result = loop_diagnose.diagnose(case["spec"])
        intended_fields = case.get("intended_fields", [])
        found = set(result["missing_fields"] + result["vague_fields"])
        patch_fields = {item["field"] for item in result["patches"]}
        if set(intended_fields) <= found:
            intended += 1
        else:
            failures.append(f"{case['id']}: intended fields not found; expected {intended_fields}, got {sorted(found)}")
        if set(intended_fields) <= patch_fields:
            replacements += 1
        if {"verification_method", "maker_checker_split", "approval_artifact"} & patch_fields:
            verifier_or_review += 1
        if not result["patches"]:
            failures.append(f"{case['id']}: no concrete replacement text")
    if len(cases) < 20:
        failures.append(f"case count below 20: {len(cases)}")
    if intended != len(cases):
        failures.append(f"intended-field detection below 20/20: {intended}/{len(cases)}")
    if replacements < 18:
        failures.append(f"replacement coverage below 18/20: {replacements}/{len(cases)}")
    if verifier_or_review < 18:
        failures.append(f"verifier/review-gate coverage below 18/20: {verifier_or_review}/{len(cases)}")
    return {"total": len(cases), "intended": intended, "replacements": replacements, "verifier_or_review": verifier_or_review, "failures": failures}


if __name__ == "__main__":
    result = run()
    print(
        f"audit_advanced_improvement_cases: intended={result['intended']}/{result['total']}; "
        f"replacements={result['replacements']}/{result['total']}; verifier_or_review={result['verifier_or_review']}/{result['total']}"
    )
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
