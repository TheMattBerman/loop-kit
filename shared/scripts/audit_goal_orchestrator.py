#!/usr/bin/env python3
"""Audit V5 Goal Orchestrator cycles and durable artifacts."""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from goal_orchestrator import build_goal_cycle, write_cycle_artifacts

CASES = ROOT / "golden" / "goal_orchestrator_cases.json"
REQUIRED_FILES = {
    "original-objective.md",
    "success-criteria.json",
    "worker-kickoff.md",
    "reviewer-prompt.md",
    "result-report.json",
    "evidence-checklist.json",
    "decision.json",
    "next-goal-prompt.md",
}


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    needs_fix_with_next = 0
    drift_cases = 0
    scheduler_connector = 0
    vague_cases = 0
    with tempfile.TemporaryDirectory(prefix="loop-kit-v5-") as tmp:
        root = Path(tmp)
        for case in cases:
            cycle = build_goal_cycle(
                case["objective"],
                result_report_text=case.get("result_report", ""),
                success_criteria=case.get("success_criteria"),
                constraints=case.get("constraints"),
                cycle_id=case["id"],
            )
            files = write_cycle_artifacts(cycle, root / case["id"])
            missing = REQUIRED_FILES - set(files)
            if missing:
                failures.append(f"{case['id']}: missing artifact files {sorted(missing)}")
            if cycle["decision"]["verdict"] != case["expected_verdict"]:
                failures.append(f"{case['id']}: expected {case['expected_verdict']}, got {cycle['decision']}")
            objective = case["objective"]
            for key in ["worker_kickoff_prompt", "reviewer_prompt"]:
                if objective not in cycle[key]:
                    failures.append(f"{case['id']}: {key} lost original objective")
            if case.get("expect_next_goal") and "Original objective:" not in cycle["next_goal_prompt"]:
                failures.append(f"{case['id']}: expected next-goal prompt with original objective")
            if not case.get("expect_next_goal") and not cycle["decision"]["complete"]:
                failures.append(f"{case['id']}: expected complete decision")
            expected_failure = case.get("expected_failure_contains")
            if expected_failure and expected_failure not in cycle["decision"]["failures"]:
                failures.append(f"{case['id']}: missing failure {expected_failure!r}, got {cycle['decision']['failures']}")
            if cycle["decision"]["verdict"] in {"needs_fix", "blocked"} and cycle["next_goal_prompt"].startswith("/goal"):
                needs_fix_with_next += 1
            if case.get("fixture_type") == "drift":
                drift_cases += 1
                if cycle["decision"]["complete"]:
                    failures.append(f"{case['id']}: drift case incorrectly completed")
            if case.get("fixture_type") in {"scheduler", "connector"}:
                scheduler_connector += 1
                expected_setup = case.get("expected_setup_contains")
                setup_text = "\n".join(cycle["decision"].get("setup_instructions", [])) + "\n" + cycle["next_goal_prompt"]
                if expected_setup and expected_setup not in setup_text:
                    failures.append(f"{case['id']}: missing setup instruction {expected_setup!r}")
                forbidden = ["installed scheduler", "created cron", "connected gmail", "authorized gmail", "connected slack"]
                if any(term in setup_text.lower() for term in forbidden):
                    failures.append(f"{case['id']}: overclaimed scheduler/connector action")
            if case.get("fixture_type") == "vague":
                vague_cases += 1
                if len(cycle["success_criteria"]) < 5:
                    failures.append(f"{case['id']}: vague goal did not produce enough measurable criteria")
    if len(cases) < 5:
        failures.append(f"goal-cycle case count below 5: {len(cases)}")
    if needs_fix_with_next < 3:
        failures.append(f"fewer than 3 failure/partial cases produced next-goal prompts: {needs_fix_with_next}")
    if drift_cases < 2:
        failures.append(f"fewer than 2 objective drift fixtures: {drift_cases}")
    if scheduler_connector < 2:
        failures.append(f"fewer than 2 scheduler/connector setup fixtures: {scheduler_connector}")
    if vague_cases < 1:
        failures.append("no vague-goal fixture proved criteria generation")
    return {"total": len(cases), "failures": failures}


if __name__ == "__main__":
    result = run()
    print(f"audit_goal_orchestrator: {result['total'] - len(result['failures'])}/{result['total']} passed")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
