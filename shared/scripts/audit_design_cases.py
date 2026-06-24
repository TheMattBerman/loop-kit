#!/usr/bin/env python3
"""Audit loop design quality against deterministic golden cases."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "shared" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import loop_onboard

CASES = ROOT / "golden" / "design_quality_cases.json"


def design_score(case, mapped):
    score = 0
    score += int(case.get("source_concrete", True) and "unknown source" not in mapped["source"])
    score += int(case.get("done_concrete", True) and "not specified" not in mapped["done"])
    score += int(case.get("verification", True))
    score += int(case.get("hard_stop", True))
    score += int(case.get("noop", True))
    score += int(case.get("approval", True))
    score += int(case.get("output_packet", True) and bool(mapped["output"]))
    score += int(case.get("first_run", True) and "manual" in mapped["trigger"].lower())
    score += int(case.get("risk_matched", True) and bool(mapped["risk"]))
    score += int(case.get("expected_archetype") == mapped["archetype"])
    return score


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    scores = []
    top1 = 0
    top3 = 0
    unsafe_total = 0
    unsafe_pass = 0
    for case in cases:
        mapped = loop_onboard.map_loop(case["input"])
        routes = [mapped["archetype"], *mapped.get("secondaries", [])]
        if case["expected_archetype"] == mapped["archetype"]:
            top1 += 1
        if case["expected_archetype"] in routes[:3]:
            top3 += 1
        score = design_score(case, mapped)
        scores.append(score)
        if score < case.get("min_score", 8):
            failures.append(f"{case['id']}: score {score}/10 for {mapped['archetype']}")
        if case.get("unsafe") or case.get("not_a_loop"):
            unsafe_total += 1
            recommendation = mapped["recommendation"].lower()
            if mapped["flags"] or "do not build" in recommendation or "prompt/checklist" in recommendation:
                unsafe_pass += 1
            else:
                failures.append(f"{case['id']}: unsafe/not-loop case was not downgraded")
    avg = sum(scores) / len(scores)
    top1_acc = top1 / len(cases)
    top3_acc = top3 / len(cases)
    if len(cases) < 30:
        failures.append(f"case count below 30: {len(cases)}")
    if avg < 8.5:
        failures.append(f"average design score below 8.5: {avg:.2f}")
    if top1_acc < 0.85:
        failures.append(f"top1 accuracy below 85%: {top1_acc:.1%}")
    if top3_acc < 0.95:
        failures.append(f"top3 accuracy below 95%: {top3_acc:.1%}")
    if unsafe_total and unsafe_pass != unsafe_total:
        failures.append("not all unsafe/not-loop cases refused or downgraded")
    return {"total": len(cases), "avg": avg, "top1": top1_acc, "top3": top3_acc, "failures": failures}


if __name__ == "__main__":
    result = run()
    print(
        f"audit_design_cases: {result['total'] - len(result['failures'])}/{result['total']} passed; "
        f"avg={result['avg']:.2f}; top1={result['top1']:.1%}; top3={result['top3']:.1%}"
    )
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
