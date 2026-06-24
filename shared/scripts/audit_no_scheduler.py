#!/usr/bin/env python3
"""Audit that V3-A emits no scheduler or external-mutation behavior."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from connectors import make_adapter
from controlled_recurrence import run_sandbox_recurrence
from graduation import evaluate_graduation
from runtime_policy import evaluate_close
from schedule_proposals import render_schedule_proposal, validate_schedule_proposal


FORBIDDEN_TERMS = [
    "cron creation",
    "recurring automation creation",
    "background job installation",
    "monitor setup",
]


def run():
    failures = []
    scheduled = evaluate_close("manual_pass", evidence=["ev-1"], verifier_results=[{"passed": True}], schedule_recommendation="scheduled")
    if scheduled["allowed"] or scheduled["schedule_recommendation"] == "scheduled":
        failures.append("runtime emitted or accepted scheduled")
    adapter = make_adapter("local_file")
    for action in ["merge", "delete", "send", "post", "publish", "deploy", "spend", "bill"]:
        plan = adapter.prepare_action(
            {
                "run_id": "run-1",
                "action_type": action,
                "target": "fixture",
                "payload": {"body": "fixture"},
                "source_snapshot_id": "snap-1",
            }
        )
        if plan["status"] not in {"blocked", "approval_valid_but_not_executable"}:
            failures.append(f"{action}: action not blocked/non-executable: {plan}")
    searchable = (ROOT / "README.md").read_text(errors="ignore").lower()
    for term in FORBIDDEN_TERMS:
        if term in searchable:
            failures.append(f"forbidden scheduler claim found: {term}")
    profile = {
        "loop_id": "no-scheduler-proof",
        "risk_level": "low",
        "read_only": True,
        "source_snapshot_ids": ["snap-1"],
        "owner": "operator",
        "stop_condition": "pause on verifier failure",
        "rollback_plan": "restore previous local artifact",
        "no_op_behavior": "write no_op reason and source proof",
        "review_cadence": "weekly",
        "monitor_plan": "local ledger review only",
        "budget_cost_guard": "pause above 5 minutes",
    }
    records = [
        {"run_id": "run-1", "loop_id": "no-scheduler-proof", "terminal_state": "manual_pass", "accepted": True, "evidence_ids": ["ev-1"]},
        {"run_id": "run-2", "loop_id": "no-scheduler-proof", "terminal_state": "manual_pass", "accepted": True, "evidence_ids": ["ev-2"]},
    ]
    costs = [{"run_id": "run-1", "loop_id": "no-scheduler-proof", "runtime_seconds": 10, "cost_estimate": "unknown", "budget_status": "ok"}]
    evaluation = evaluate_graduation(profile, records, costs)
    proposal = render_schedule_proposal(evaluation, profile)
    proposal_check = validate_schedule_proposal(proposal, evaluation=evaluation)
    if not proposal_check["valid"]:
        failures.append(f"schedule proposal artifact invalid: {proposal_check}")
    if proposal.get("creates_schedule") is not False:
        failures.append("schedule proposal attempted schedule creation")
    controlled = run_sandbox_recurrence(
        proposal,
        [
            {
                "run_id": "run-1",
                "loop_id": "no-scheduler-proof",
                "cadence_tick": "tick-1",
                "terminal_state": "manual_pass",
                "evidence_ids": ["ev-1"],
                "runtime_seconds": 10,
                "source_available": True,
                "source_drift_detected": False,
                "approval_required": False,
                "approval_artifact_id": "",
                "budget_status": "ok",
            }
        ],
    )
    if controlled.get("creates_schedule") is not False:
        failures.append("controlled recurrence attempted schedule creation")
    return {"passed": not failures, "failures": failures}


if __name__ == "__main__":
    result = run()
    print("audit_no_scheduler: PASS" if result["passed"] else "audit_no_scheduler: FAIL")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
