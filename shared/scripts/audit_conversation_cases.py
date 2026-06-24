#!/usr/bin/env python3
"""Audit beginner conversation routing and approval-boundary behavior."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "shared" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import loop_onboard
import plain_language

CASES = ROOT / "golden" / "conversation_cases.json"
JARGON = re.compile(r"\bR[0-4]\b|\bL[0-4]\b|archetype|downgrade-to-prompt|not-a-loop|fix-then-go|verdict|maturity|risk", re.I)


def _ready(mapped):
    return not mapped["flags"] and "unknown source" not in mapped["source"] and "not specified" not in mapped["done"]


def run_case(case):
    mapped = loop_onboard.map_loop(case["input"])
    packet = plain_language.beginner_packet(case["input"])
    failures = []
    expected_route = case.get("expected_route")
    routes = [mapped["archetype"], *mapped.get("secondaries", [])]
    if expected_route and expected_route not in routes:
        failures.append(f"route expected {expected_route}, got {routes}")
    blob = json.dumps(packet)
    if case.get("beginner", True) and JARGON.search(blob):
        failures.append("beginner packet exposed internal jargon")
    if len(packet["questions"]) > 3 and not case.get("full_walkthrough"):
        failures.append("asked more than 3 blocker questions")
    boundary = " ".join(packet["checks_with_you_first"]).lower()
    if not all(word in boundary for word in ["sends", "publishes", "spends"]):
        failures.append("approval boundary missing from beginner packet")
    if case.get("unsafe") and _ready(mapped):
        failures.append("unsafe prompt received ready verdict")
    if case.get("must_flag"):
        for flag in case["must_flag"]:
            if flag not in mapped["flags"]:
                failures.append(f"missing flag {flag}")
    return failures


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    route_passes = 0
    beginner_count = 0
    beginner_jargon_free = 0
    approval_count = 0
    approval_passes = 0
    unsafe_false_ready = 0
    unsafe_count = 0
    for case in cases:
        case_failures = run_case(case)
        mapped = loop_onboard.map_loop(case["input"])
        routes = [mapped["archetype"], *mapped.get("secondaries", [])]
        if case.get("expected_route") in routes:
            route_passes += 1
        packet = plain_language.beginner_packet(case["input"])
        if case.get("beginner", True):
            beginner_count += 1
            if not JARGON.search(json.dumps(packet)):
                beginner_jargon_free += 1
        approval_count += 1
        if packet["checks_with_you_first"]:
            approval_passes += 1
        if case.get("unsafe"):
            unsafe_count += 1
            if not _ready(mapped):
                unsafe_false_ready += 1
        if case_failures:
            failures.append(f"{case['id']}: {'; '.join(case_failures)}")
    route_accuracy = route_passes / len(cases)
    if len(cases) < 30:
        failures.append(f"case count below 30: {len(cases)}")
    if route_accuracy < 0.95:
        failures.append(f"route accuracy below 95%: {route_accuracy:.1%}")
    if beginner_count and beginner_jargon_free != beginner_count:
        failures.append("not all beginner outputs were jargon-free")
    if approval_passes != approval_count:
        failures.append("not all outputs preserved approval boundary")
    if unsafe_count and unsafe_false_ready != unsafe_count:
        failures.append("unsafe prompts had false ready verdicts")
    return {
        "passed": len(cases) - len(failures),
        "total": len(cases),
        "route_accuracy": route_accuracy,
        "failures": failures,
    }


if __name__ == "__main__":
    result = run()
    print(f"audit_conversation_cases: {result['total'] - len(result['failures'])}/{result['total']} passed; route_accuracy={result['route_accuracy']:.1%}")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
