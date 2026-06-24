"""Runtime policy gates for supervised loop first runs."""

import re


TERMINAL_STATES = {
    "manual_pass",
    "fix_then_rerun",
    "no_op",
    "blocked",
    "do_not_schedule",
    "failed_verification",
    "approval_required",
    "exhausted",
}

EXTERNAL_ACTIONS = [
    "send",
    "post",
    "publish",
    "deploy",
    "merge",
    "delete",
    "spend",
    "bill",
    "customer-facing update",
]

EXTERNAL_ACTION_RE = re.compile(
    r"\b(send|post|publish|deploy|merge|delete|spend|bill)(?:s|es|ed|ing)?\b|customer-facing update",
    re.I,
)


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def detect_external_actions(actions):
    found = set()
    for action in _as_list(actions):
        text = str(action or "")
        for match in EXTERNAL_ACTION_RE.finditer(text):
            found.add(match.group(0).lower())
    return sorted(found)


def has_evidence(evidence):
    return bool([item for item in _as_list(evidence) if str(item).strip()])


def verifier_results_passed(results):
    normalized = _as_list(results)
    if not normalized:
        return False
    for result in normalized:
        if isinstance(result, dict):
            if not result.get("passed"):
                return False
        elif str(result).strip().lower() not in {"pass", "passed", "true", "ok"}:
            return False
    return True


def evaluate_action(actions, approval_artifact=None):
    external = detect_external_actions(actions)
    if external and not str(approval_artifact or "").strip():
        return {
            "allowed": False,
            "requires_approval": True,
            "external_actions": external,
            "reason": "external action requires approval artifact",
        }
    return {
        "allowed": True,
        "requires_approval": bool(external),
        "external_actions": external,
        "reason": "ok",
    }


def evaluate_close(
    terminal_state,
    evidence=None,
    verifier_results=None,
    no_op_reason=None,
    actions=None,
    approval_artifact=None,
    review_gate_required=False,
    review_gate_passed=False,
    approval_artifact_required=False,
    schedule_recommendation=None,
):
    """Validate a checkpoint close request and graduation recommendation."""
    state = str(terminal_state or "").strip()
    failures = []
    if state not in TERMINAL_STATES:
        failures.append(f"invalid terminal_state:{state or 'missing'}")
    if state == "manual_pass":
        if not has_evidence(evidence):
            failures.append("manual_pass requires evidence")
        if not verifier_results_passed(verifier_results):
            failures.append("manual_pass requires passing verifier results")
    if state == "no_op" and not str(no_op_reason or "").strip():
        failures.append("no_op requires a reason")

    action_policy = evaluate_action(actions, approval_artifact)
    if not action_policy["allowed"]:
        failures.append(action_policy["reason"])

    requested_schedule = str(schedule_recommendation or "").strip()
    if requested_schedule == "scheduled":
        failures.append("runtime never emits scheduled")
    if requested_schedule and requested_schedule != "safe_to_consider_scheduling":
        failures.append(f"invalid schedule_recommendation:{requested_schedule}")
    if requested_schedule == "safe_to_consider_scheduling" and state != "manual_pass":
        failures.append("schedule promotion requires manual_pass")
    if state == "manual_pass" and review_gate_required and not review_gate_passed:
        failures.append("schedule promotion requires review gate")
    if approval_artifact_required and state == "manual_pass" and not str(approval_artifact or "").strip():
        failures.append("schedule promotion requires approval artifact")

    can_recommend = (
        state == "manual_pass"
        and not failures
        and (not review_gate_required or review_gate_passed)
        and (not approval_artifact_required or bool(str(approval_artifact or "").strip()))
    )
    return {
        "allowed": not failures,
        "terminal_state": state,
        "failures": failures,
        "external_actions": action_policy["external_actions"],
        "approval_required": action_policy["requires_approval"],
        "schedule_recommendation": "safe_to_consider_scheduling" if can_recommend else "do_not_schedule",
    }
