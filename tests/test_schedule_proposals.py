import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from graduation import evaluate_graduation, make_acceptance_record, make_cost_record
from schedule_proposals import render_schedule_proposal, validate_schedule_proposal


def ready_profile():
    return {
        "loop_id": "loop-proposal",
        "risk_level": "medium",
        "source_snapshot_ids": ["snap-1"],
        "owner": "operator",
        "stop_condition": "pause on verifier failure",
        "rollback_plan": "restore previous local output",
        "no_op_behavior": "write no_op reason and source proof",
        "review_cadence": "weekly",
        "monitor_plan": "local ledger review only",
        "budget_cost_guard": "pause above 10 minutes",
    }


def ready_records():
    return [
        make_acceptance_record("run-1", "loop-proposal", "manual_pass", True, ["ev-1"]),
        make_acceptance_record("run-2", "loop-proposal", "manual_pass", True, ["ev-2"]),
        make_acceptance_record("run-3", "loop-proposal", "manual_pass", True, ["ev-3"]),
    ]


def test_schedule_proposal_is_artifact_only():
    profile = ready_profile()
    evaluation = evaluate_graduation(profile, ready_records(), [make_cost_record("run-1", "loop-proposal", 10)])
    proposal = render_schedule_proposal(evaluation, profile)
    result = validate_schedule_proposal(proposal, evaluation=evaluation)
    assert result["valid"]
    assert proposal["creates_schedule"] is False
    assert proposal["recommendation"] == "safe_to_consider_scheduling"


def test_schedule_proposal_blocks_missing_evidence():
    profile = ready_profile()
    evaluation = evaluate_graduation(profile, ready_records(), [make_cost_record("run-1", "loop-proposal", 10)])
    proposal = render_schedule_proposal(evaluation, profile)
    proposal["evidence_window"]["evidence_ids"] = []
    result = validate_schedule_proposal(proposal, evaluation=evaluation)
    assert not result["valid"]
    assert "proposal requires evidence ids and source snapshot ids" in result["failures"]


def test_schedule_proposal_rejects_schedule_creation():
    profile = ready_profile()
    evaluation = evaluate_graduation(profile, ready_records(), [make_cost_record("run-1", "loop-proposal", 10)])
    proposal = render_schedule_proposal(evaluation, profile)
    proposal["creates_schedule"] = True
    result = validate_schedule_proposal(proposal, evaluation=evaluation)
    assert not result["valid"]
    assert "proposal must not create a schedule" in result["failures"]
