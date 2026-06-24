import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from controlled_recurrence import make_run_record, run_sandbox_recurrence, summarize_controlled_runs


def proposal(loop_id="loop-test"):
    return {
        "proposal_id": "proposal-test",
        "loop_id": loop_id,
        "recommendation": "safe_to_consider_scheduling",
        "evidence_window": {"run_count": 3, "evidence_ids": ["ev-a"], "source_snapshot_ids": ["snap-a"]},
        "successful_supervised_run_count": 3,
        "acceptance_rate": 1.0,
        "failure_rate": 0.0,
        "owner": "operator",
        "review_cadence": "weekly",
        "monitor_plan": "local ledger review",
        "stop_condition": "pause on failure",
        "rollback_no_op_behavior": {"rollback_plan": "restore previous", "no_op_behavior": "write no_op proof"},
        "budget_cost_guard": "pause above 5 minutes",
        "approval_requirement": {"required": False, "approval_artifact_id": "", "maker_checker_review_passed": False},
        "expires_at": "2026-07-01T00:00:00+00:00",
        "creates_schedule": False,
    }


def test_sandbox_recurrence_does_not_create_schedule():
    runs = [
        make_run_record("run-1", "loop-test", "tick-1", "manual_pass", ["ev-1"], 10),
        make_run_record("run-2", "loop-test", "tick-2", "manual_pass", ["ev-2"], 10),
    ]
    result = run_sandbox_recurrence(proposal(), runs, expected_runtime_seconds=20)
    assert result["creates_schedule"] is False
    assert result["final_status"] == "active"
    assert result["valid_close_rate"] == 1.0


def test_sandbox_recurrence_pauses_on_failure():
    runs = [
        make_run_record("run-1", "loop-test", "tick-1", "manual_pass", ["ev-1"], 10),
        make_run_record("run-2", "loop-test", "tick-2", "failed_verification", ["ev-2"], 10),
        make_run_record("run-3", "loop-test", "tick-3", "manual_pass", ["ev-3"], 10),
    ]
    result = run_sandbox_recurrence(proposal(), runs, expected_runtime_seconds=20)
    assert result["final_status"] == "paused"
    assert "terminal state requires pause:failed_verification" in result["ledger"][1]["pause_reasons"]
    assert result["ledger"][2]["alert_state"] == "skipped_after_pause"


def test_sandbox_recurrence_pauses_on_missing_approval():
    runs = [make_run_record("run-1", "loop-test", "tick-1", "approval_required", ["ev-1"], 10, approval_required=True)]
    result = run_sandbox_recurrence(proposal(), runs, expected_runtime_seconds=20)
    assert result["final_status"] == "paused"
    assert "missing approval artifact" in result["ledger"][0]["pause_reasons"]


def test_sandbox_summary_counts_valid_closes():
    clean = run_sandbox_recurrence(
        proposal("loop-a"),
        [make_run_record("run-1", "loop-a", "tick-1", "manual_pass", ["ev-1"], 10)],
        expected_runtime_seconds=20,
    )
    paused = run_sandbox_recurrence(
        proposal("loop-b"),
        [make_run_record("run-1", "loop-b", "tick-1", "manual_pass", ["ev-1"], 30)],
        expected_runtime_seconds=20,
    )
    summary = summarize_controlled_runs([clean, paused])
    assert summary["loop_count"] == 2
    assert summary["paused_loops"] == 1
    assert summary["creates_schedule"] is False
