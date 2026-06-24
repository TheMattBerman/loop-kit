#!/usr/bin/env python3
"""Audit fake connector capability and approval policy cases."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from runtime_policy import evaluate_action

CASES = ROOT / "golden" / "connector_policy_cases.json"
APPROVAL_ACTIONS = {"send", "post", "publish", "deploy", "merge", "delete", "spend", "bill", "customer-facing update"}


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    for case in cases:
        adapter = case.get("adapter", {})
        actions = case.get("actions", [])
        if not {"allowed", "forbidden", "approval_required"} <= set(adapter):
            failures.append(f"{case['id']}: adapter missing permission declaration")
        if case.get("missing_auth"):
            if case.get("expected") != "blocked":
                failures.append(f"{case['id']}: missing auth must block")
            continue
        if case.get("unknown_capability") or case.get("capability_mismatch"):
            if case.get("expected") != "blocked":
                failures.append(f"{case['id']}: unknown/capability mismatch must block")
            continue
        if any(str(action).lower().strip().startswith("draft") for action in actions) and not case.get("draft_artifact"):
            failures.append(f"{case['id']}: draft action missing local draft artifact")
        policy = evaluate_action(actions, approval_artifact=case.get("approval_artifact"))
        write_actions = {action for action in actions for token in APPROVAL_ACTIONS if token in action.lower()}
        if write_actions and policy["allowed"] and not case.get("approval_artifact"):
            failures.append(f"{case['id']}: unauthorized connector action allowed")
        if case.get("expected") == "blocked" and policy["allowed"]:
            failures.append(f"{case['id']}: expected blocked")
        if case.get("expected") == "allowed" and not policy["allowed"]:
            failures.append(f"{case['id']}: expected allowed, got {policy}")
        if "read" in adapter.get("allowed", []) and not case.get("source_snapshot"):
            failures.append(f"{case['id']}: read-only adapter missing source snapshot metadata")
    if len(cases) < 30:
        failures.append(f"connector policy case count below 30: {len(cases)}")
    return {"total": len(cases), "failures": failures}


if __name__ == "__main__":
    result = run()
    print(f"audit_connector_policy: {result['total'] - len(result['failures'])}/{result['total']} passed")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
