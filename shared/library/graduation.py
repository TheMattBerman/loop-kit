"""Graduation scoring and ledgers for schedule-readiness proposals."""

from datetime import datetime, timezone

from source_safety import stable_id


FAILURE_STATES = {"blocked", "fix_then_rerun", "failed_verification", "exhausted", "do_not_schedule"}


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def make_acceptance_record(
    run_id,
    loop_id,
    terminal_state,
    accepted,
    evidence_ids=None,
    reviewer=None,
    checker=None,
    observed_at=None,
):
    return {
        "run_id": str(run_id),
        "loop_id": str(loop_id),
        "terminal_state": str(terminal_state),
        "accepted": bool(accepted),
        "evidence_ids": [str(item) for item in (evidence_ids or [])],
        "reviewer": reviewer or "",
        "checker": checker or "",
        "observed_at": observed_at or utc_now(),
    }


def make_cost_record(
    run_id,
    loop_id,
    runtime_seconds,
    cost_estimate="unknown",
    budget_status="ok",
    observed_at=None,
):
    return {
        "run_id": str(run_id),
        "loop_id": str(loop_id),
        "runtime_seconds": float(runtime_seconds),
        "cost_estimate": cost_estimate,
        "budget_status": str(budget_status or "unknown"),
        "observed_at": observed_at or utc_now(),
    }


def summarize_ledgers(acceptance_records, cost_records=None, loop_id=None):
    records = [record for record in acceptance_records if loop_id is None or record.get("loop_id") == loop_id]
    costs = [record for record in (cost_records or []) if loop_id is None or record.get("loop_id") == loop_id]
    total = len(records)
    accepted = [record for record in records if record.get("accepted") is True]
    successful = [record for record in accepted if record.get("terminal_state") == "manual_pass"]
    failures = [record for record in records if record.get("terminal_state") in FAILURE_STATES]
    evidence_ids = sorted(
        {
            str(evidence_id)
            for record in records
            for evidence_id in record.get("evidence_ids", [])
            if str(evidence_id).strip()
        }
    )
    missing_evidence = [
        record.get("run_id")
        for record in successful
        if not [item for item in record.get("evidence_ids", []) if str(item).strip()]
    ]
    unstable_cost_runs = [
        record.get("run_id")
        for record in costs
        if record.get("budget_status") != "ok" or float(record.get("runtime_seconds", 0)) <= 0
    ]
    return {
        "loop_id": loop_id or (records[0].get("loop_id") if records else ""),
        "total_runs": total,
        "accepted_runs": len(accepted),
        "successful_supervised_runs": len(successful),
        "failed_runs": len(failures),
        "acceptance_rate": round(len(accepted) / total, 4) if total else 0.0,
        "failure_rate": round(len(failures) / total, 4) if total else 0.0,
        "evidence_ids": evidence_ids,
        "reviewers": sorted({record.get("reviewer") for record in records if record.get("reviewer")}),
        "checkers": sorted({record.get("checker") for record in records if record.get("checker")}),
        "cost_records": len(costs),
        "unstable_cost_runs": unstable_cost_runs,
        "missing_evidence_runs": missing_evidence,
    }


def required_supervised_runs(profile):
    if profile.get("min_supervised_runs"):
        return int(profile["min_supervised_runs"])
    if profile.get("risk_level") == "low" and profile.get("read_only") is True:
        return 2
    return 3


def evaluate_graduation(profile, acceptance_records, cost_records=None):
    loop_id = str(profile.get("loop_id") or "")
    summary = summarize_ledgers(acceptance_records, cost_records, loop_id=loop_id)
    failures = []
    min_runs = required_supervised_runs(profile)
    min_acceptance_rate = float(profile.get("min_acceptance_rate", 0.7))
    max_failure_rate = float(profile.get("max_failure_rate", 0.2))

    if not loop_id:
        failures.append("missing loop id")
    if not profile.get("source_snapshot_ids"):
        failures.append("missing source snapshot")
    if not profile.get("owner"):
        failures.append("missing owner")
    if not profile.get("stop_condition"):
        failures.append("missing stop condition")
    if not (profile.get("rollback_plan") and profile.get("no_op_behavior")):
        failures.append("missing rollback/no-op behavior")
    if summary["successful_supervised_runs"] < min_runs:
        failures.append("insufficient supervised successful runs")
    if summary["acceptance_rate"] < min_acceptance_rate:
        failures.append("acceptance rate below threshold")
    if summary["failure_rate"] > max_failure_rate:
        failures.append("failure rate above threshold")
    if not summary["evidence_ids"] or summary["missing_evidence_runs"]:
        failures.append("missing evidence")
    if profile.get("source_drift_detected"):
        failures.append("source drift detected")
    if summary["unstable_cost_runs"]:
        failures.append("unstable cost")
    high_risk = profile.get("risk_level") == "high" or profile.get("external_actions") is True
    if high_risk and not profile.get("maker_checker_review_passed"):
        failures.append("high-risk graduation requires maker/checker review")
    if profile.get("external_actions") is True and profile.get("approval_artifact_required", True) and not profile.get("approval_artifact_id"):
        failures.append("external-action proposal requires approval artifact")

    eligible = not failures
    return {
        "eligible": eligible,
        "recommendation": "safe_to_consider_scheduling" if eligible else "do_not_schedule",
        "failures": failures,
        "metrics": summary,
        "required_supervised_runs": min_runs,
        "graduation_id": stable_id("grad", f"{loop_id}:{summary['total_runs']}:{summary['acceptance_rate']}:{summary['failure_rate']}"),
    }
