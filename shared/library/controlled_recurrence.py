"""Sandbox controlled recurrence without installing real schedules."""

from datetime import datetime, timezone

from runtime_policy import TERMINAL_STATES
from schedule_proposals import validate_schedule_proposal
from source_safety import stable_id


FAILURE_STATES = {"blocked", "fix_then_rerun", "failed_verification", "exhausted", "do_not_schedule"}
REQUIRED_RUN_FIELDS = [
    "run_id",
    "loop_id",
    "cadence_tick",
    "terminal_state",
    "evidence_ids",
    "runtime_seconds",
    "source_available",
    "source_drift_detected",
    "approval_required",
    "approval_artifact_id",
    "budget_status",
]


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def make_run_record(
    run_id,
    loop_id,
    cadence_tick,
    terminal_state,
    evidence_ids=None,
    runtime_seconds=1,
    source_available=True,
    source_drift_detected=False,
    approval_required=False,
    approval_artifact_id="",
    budget_status="ok",
    observed_at=None,
):
    return {
        "run_id": str(run_id),
        "loop_id": str(loop_id),
        "cadence_tick": str(cadence_tick),
        "terminal_state": str(terminal_state),
        "evidence_ids": [str(item) for item in (evidence_ids or [])],
        "runtime_seconds": float(runtime_seconds),
        "source_available": bool(source_available),
        "source_drift_detected": bool(source_drift_detected),
        "approval_required": bool(approval_required),
        "approval_artifact_id": str(approval_artifact_id or ""),
        "budget_status": str(budget_status or "unknown"),
        "observed_at": observed_at or utc_now(),
    }


def validate_run_record(record, expected_loop_id=None):
    failures = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["run record missing or malformed"]}
    missing = [field for field in REQUIRED_RUN_FIELDS if field not in record]
    failures.extend(f"missing:{field}" for field in missing)
    if expected_loop_id and record.get("loop_id") != expected_loop_id:
        failures.append("wrong loop id")
    if record.get("terminal_state") not in TERMINAL_STATES:
        failures.append("invalid terminal state")
    if not [item for item in record.get("evidence_ids", []) if str(item).strip()]:
        failures.append("missing evidence")
    if float(record.get("runtime_seconds", 0)) <= 0:
        failures.append("invalid runtime")
    if record.get("approval_required") and not record.get("approval_artifact_id"):
        failures.append("missing approval artifact")
    return {"valid": not failures, "failures": failures}


def monitor_run(record, proposal, expected_runtime_seconds=None):
    failures = validate_run_record(record, expected_loop_id=proposal.get("loop_id"))["failures"]
    if record.get("terminal_state") in FAILURE_STATES:
        failures.append(f"terminal state requires pause:{record.get('terminal_state')}")
    if record.get("source_available") is False:
        failures.append("missing source")
    if record.get("source_drift_detected") is True:
        failures.append("source drift detected")
    if record.get("budget_status") != "ok":
        failures.append("budget breach")
    if expected_runtime_seconds and float(record.get("runtime_seconds", 0)) > float(expected_runtime_seconds):
        failures.append("runtime breach")
    status = "paused" if failures else "active"
    return {
        "status": status,
        "alert_state": "needs_attention" if failures else "ok",
        "pause_reasons": sorted(set(failures)),
    }


def run_sandbox_recurrence(proposal, run_records, expected_runtime_seconds=None):
    proposal_check = validate_schedule_proposal(proposal)
    ledger = []
    paused = False
    silent_failures = 0
    for record in run_records:
        if paused:
            ledger.append(
                {
                    "ledger_id": stable_id("rec", f"skipped:{record.get('run_id')}"),
                    "run_id": record.get("run_id"),
                    "loop_id": proposal.get("loop_id"),
                    "status": "paused",
                    "alert_state": "skipped_after_pause",
                    "terminal_state": "blocked",
                    "evidence_ids": record.get("evidence_ids", []),
                    "pause_reasons": ["previous run paused recurrence"],
                }
            )
            continue
        monitor = monitor_run(record, proposal, expected_runtime_seconds=expected_runtime_seconds)
        paused = monitor["status"] == "paused"
        if monitor["alert_state"] != "ok" and not monitor["pause_reasons"]:
            silent_failures += 1
        ledger.append(
            {
                "ledger_id": stable_id("rec", f"{record.get('run_id')}:{monitor['status']}:{record.get('terminal_state')}"),
                "run_id": record.get("run_id"),
                "loop_id": record.get("loop_id"),
                "cadence_tick": record.get("cadence_tick"),
                "status": monitor["status"],
                "alert_state": monitor["alert_state"],
                "terminal_state": record.get("terminal_state"),
                "evidence_ids": record.get("evidence_ids", []),
                "runtime_seconds": record.get("runtime_seconds"),
                "pause_reasons": monitor["pause_reasons"],
            }
        )
    valid_closes = [
        item
        for item in ledger
        if item.get("terminal_state") in TERMINAL_STATES and item.get("evidence_ids")
    ]
    return {
        "mode": "sandbox_local_controlled",
        "creates_schedule": False,
        "proposal_valid": proposal_check["valid"],
        "proposal_failures": proposal_check["failures"],
        "run_count": len(run_records),
        "ledger": ledger,
        "valid_close_rate": round(len(valid_closes) / len(run_records), 4) if run_records else 0.0,
        "silent_failures": silent_failures,
        "final_status": "paused" if any(item["status"] == "paused" for item in ledger) else "active",
    }


def summarize_controlled_runs(results):
    total_runs = sum(result.get("run_count", 0) for result in results)
    all_ledger = [item for result in results for item in result.get("ledger", [])]
    valid_closes = [item for item in all_ledger if item.get("terminal_state") in TERMINAL_STATES and item.get("evidence_ids")]
    paused = [result for result in results if result.get("final_status") == "paused"]
    return {
        "loop_count": len(results),
        "total_runs": total_runs,
        "valid_close_rate": round(len(valid_closes) / total_runs, 4) if total_runs else 0.0,
        "paused_loops": len(paused),
        "silent_failures": sum(result.get("silent_failures", 0) for result in results),
        "creates_schedule": any(result.get("creates_schedule") for result in results),
    }
