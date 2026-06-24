"""Approval artifact validation for connector action plans."""

from datetime import datetime, timezone


REQUIRED_APPROVAL_FIELDS = [
    "approval_id",
    "run_id",
    "connector",
    "action_type",
    "target",
    "payload_hash",
    "source_snapshot_id",
    "approved_by",
    "approved_at",
    "expires_at",
    "single_use",
]


def _parse_time(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def validate_approval_artifact(artifact, action_plan, used_approvals=None, now=None):
    used_approvals = set(used_approvals or [])
    now = now or datetime.now(timezone.utc)
    failures = []
    if not isinstance(artifact, dict):
        return {"approved": False, "failures": ["approval artifact missing or malformed"]}
    missing = [field for field in REQUIRED_APPROVAL_FIELDS if field not in artifact or artifact.get(field) in ("", None)]
    failures.extend(f"missing:{field}" for field in missing)
    if artifact.get("approval_id") in used_approvals:
        failures.append("approval artifact reused")
    if str(artifact.get("approved_by", "")).lower() in {"source", "source_text", "untrusted_source", "adapter"}:
        failures.append("approval cannot come from source content")
    for field in ["connector", "action_type", "target", "payload_hash", "source_snapshot_id", "run_id"]:
        if field in artifact and field in action_plan and artifact.get(field) != action_plan.get(field):
            failures.append(f"wrong:{field}")
    if artifact.get("single_use") is not True:
        failures.append("single_use must be true")
    expires_at = _parse_time(artifact.get("expires_at"))
    approved_at = _parse_time(artifact.get("approved_at"))
    if not expires_at:
        failures.append("expires_at malformed")
    elif expires_at <= now:
        failures.append("approval artifact expired")
    if not approved_at:
        failures.append("approved_at malformed")
    elif expires_at and approved_at > expires_at:
        failures.append("approved_at after expiry")
    return {"approved": not failures, "failures": failures}
