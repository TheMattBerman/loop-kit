"""Schedule-readiness proposal artifacts that do not schedule anything."""

from datetime import datetime, timedelta, timezone

from source_safety import stable_id


REQUIRED_PROPOSAL_FIELDS = [
    "proposal_id",
    "loop_id",
    "recommendation",
    "evidence_window",
    "successful_supervised_run_count",
    "acceptance_rate",
    "failure_rate",
    "owner",
    "review_cadence",
    "monitor_plan",
    "stop_condition",
    "rollback_no_op_behavior",
    "budget_cost_guard",
    "approval_requirement",
    "expires_at",
    "creates_schedule",
]


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def parse_time(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def render_schedule_proposal(evaluation, profile, now=None, ttl_days=14):
    now = now or utc_now()
    metrics = evaluation.get("metrics", {})
    evidence_ids = metrics.get("evidence_ids", [])
    evidence_window = {
        "run_count": metrics.get("total_runs", 0),
        "evidence_ids": evidence_ids,
        "source_snapshot_ids": profile.get("source_snapshot_ids", []),
    }
    payload = {
        "loop_id": profile.get("loop_id", ""),
        "recommendation": evaluation.get("recommendation", "do_not_schedule"),
        "evidence_window": evidence_window,
        "successful_supervised_run_count": metrics.get("successful_supervised_runs", 0),
        "acceptance_rate": metrics.get("acceptance_rate", 0.0),
        "failure_rate": metrics.get("failure_rate", 0.0),
        "owner": profile.get("owner", ""),
        "review_cadence": profile.get("review_cadence", ""),
        "monitor_plan": profile.get("monitor_plan", ""),
        "stop_condition": profile.get("stop_condition", ""),
        "rollback_no_op_behavior": {
            "rollback_plan": profile.get("rollback_plan", ""),
            "no_op_behavior": profile.get("no_op_behavior", ""),
        },
        "budget_cost_guard": profile.get("budget_cost_guard", ""),
        "approval_requirement": {
            "required": bool(profile.get("external_actions") or profile.get("approval_artifact_required")),
            "approval_artifact_id": profile.get("approval_artifact_id", ""),
            "maker_checker_review_passed": bool(profile.get("maker_checker_review_passed")),
        },
        "expires_at": (now + timedelta(days=ttl_days)).isoformat(),
        "creates_schedule": False,
        "blocked_reasons": evaluation.get("failures", []),
    }
    payload["proposal_id"] = stable_id("proposal", repr(sorted(payload.items())))
    return payload


def validate_schedule_proposal(proposal, evaluation=None, now=None):
    now = now or utc_now()
    failures = []
    if not isinstance(proposal, dict):
        return {"valid": False, "failures": ["proposal missing or malformed"]}
    missing = [field for field in REQUIRED_PROPOSAL_FIELDS if field not in proposal or proposal.get(field) in ("", None)]
    failures.extend(f"missing:{field}" for field in missing)
    if proposal.get("creates_schedule") is not False:
        failures.append("proposal must not create a schedule")
    if proposal.get("recommendation") == "scheduled":
        failures.append("proposal must never emit scheduled")
    if proposal.get("recommendation") not in {"safe_to_consider_scheduling", "do_not_schedule"}:
        failures.append("invalid recommendation")
    expires_at = parse_time(proposal.get("expires_at"))
    if not expires_at:
        failures.append("expires_at malformed")
    elif expires_at <= now:
        failures.append("proposal expired")
    evidence_window = proposal.get("evidence_window") or {}
    if not evidence_window.get("evidence_ids") or not evidence_window.get("source_snapshot_ids"):
        failures.append("proposal requires evidence ids and source snapshot ids")
    if proposal.get("recommendation") == "safe_to_consider_scheduling":
        if proposal.get("successful_supervised_run_count", 0) < 2:
            failures.append("insufficient supervised successful runs")
        if float(proposal.get("acceptance_rate", 0.0)) < 0.7:
            failures.append("acceptance rate below threshold")
        if float(proposal.get("failure_rate", 0.0)) > 0.2:
            failures.append("failure rate above threshold")
        approval = proposal.get("approval_requirement") or {}
        if approval.get("required") and not approval.get("approval_artifact_id"):
            failures.append("approval artifact required")
        if approval.get("required") and not approval.get("maker_checker_review_passed"):
            failures.append("maker/checker review required")
    if evaluation and proposal.get("recommendation") != evaluation.get("recommendation"):
        failures.append("proposal recommendation does not match evaluation")
    return {"valid": not failures, "failures": failures}
