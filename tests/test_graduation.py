import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from graduation import evaluate_graduation, make_acceptance_record, make_cost_record, summarize_ledgers


def test_graduation_requires_repeated_accepted_evidence():
    profile = {
        "loop_id": "loop-test",
        "risk_level": "medium",
        "source_snapshot_ids": ["snap-1"],
        "owner": "operator",
        "stop_condition": "pause on failure",
        "rollback_plan": "restore previous",
        "no_op_behavior": "write no_op proof",
    }
    records = [
        make_acceptance_record("run-1", "loop-test", "manual_pass", True, ["ev-1"]),
        make_acceptance_record("run-2", "loop-test", "manual_pass", True, ["ev-2"]),
        make_acceptance_record("run-3", "loop-test", "manual_pass", True, ["ev-3"]),
    ]
    costs = [make_cost_record("run-1", "loop-test", 10)]
    result = evaluate_graduation(profile, records, costs)
    assert result["eligible"]
    assert result["recommendation"] == "safe_to_consider_scheduling"


def test_graduation_blocks_low_acceptance_rate():
    profile = {
        "loop_id": "loop-test",
        "risk_level": "medium",
        "source_snapshot_ids": ["snap-1"],
        "owner": "operator",
        "stop_condition": "pause on failure",
        "rollback_plan": "restore previous",
        "no_op_behavior": "write no_op proof",
    }
    records = [
        make_acceptance_record("run-1", "loop-test", "manual_pass", True, ["ev-1"]),
        make_acceptance_record("run-2", "loop-test", "manual_pass", False, ["ev-2"]),
        make_acceptance_record("run-3", "loop-test", "manual_pass", False, ["ev-3"]),
    ]
    result = evaluate_graduation(profile, records, [make_cost_record("run-1", "loop-test", 10)])
    assert not result["eligible"]
    assert "acceptance rate below threshold" in result["failures"]


def test_high_risk_requires_review_and_approval_artifact():
    profile = {
        "loop_id": "loop-test",
        "risk_level": "high",
        "external_actions": True,
        "source_snapshot_ids": ["snap-1"],
        "owner": "operator",
        "stop_condition": "pause on failure",
        "rollback_plan": "restore previous",
        "no_op_behavior": "write no_op proof",
    }
    records = [
        make_acceptance_record("run-1", "loop-test", "manual_pass", True, ["ev-1"]),
        make_acceptance_record("run-2", "loop-test", "manual_pass", True, ["ev-2"]),
        make_acceptance_record("run-3", "loop-test", "manual_pass", True, ["ev-3"]),
    ]
    result = evaluate_graduation(profile, records, [make_cost_record("run-1", "loop-test", 10)])
    assert not result["eligible"]
    assert "high-risk graduation requires maker/checker review" in result["failures"]
    assert "external-action proposal requires approval artifact" in result["failures"]


def test_ledger_summary_tracks_failure_and_cost():
    records = [
        make_acceptance_record("run-1", "loop-test", "manual_pass", True, ["ev-1"]),
        make_acceptance_record("run-2", "loop-test", "failed_verification", False, ["ev-2"]),
    ]
    costs = [make_cost_record("run-2", "loop-test", 0, budget_status="over_budget")]
    summary = summarize_ledgers(records, costs, loop_id="loop-test")
    assert summary["accepted_runs"] == 1
    assert summary["failed_runs"] == 1
    assert summary["unstable_cost_runs"] == ["run-2"]
