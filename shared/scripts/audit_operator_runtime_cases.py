#!/usr/bin/env python3
"""Run local first-run fixture loops through checkpoint/verifier close gates."""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from checkpoints import close_checkpoint, init_checkpoint
from verifiers import REGISTRY, run_verifiers

CASES = ROOT / "golden" / "operator_runtime_cases.json"


def write_spec(path, case):
    fields = {
        "name": case["id"],
        "source_of_truth": case["source"],
        "done_criteria": case["done"],
        "verification_method": case["verification"],
        "approval_boundary": case["approval_boundary"],
        "hard_stops": "stop after one local fixture pass or any missing approval",
        "no_op_condition": "close no_op if the fixture source has no records",
        "output_packet": "output-packet.md with evidence, verifier results, blockers, and next decision",
        "first_manual_dry_run": "required before repeat",
        "state_location": ".loop-kit/STATE.md",
        "tools_and_permissions": "read local fixtures and write local checkpoint artifacts only",
        "run_artifacts": "checkpoint.json source-freeze.md output-packet.md blockers.md approval-request.yaml",
        "maker_checker_split": "checker must review consequential or subjective output before promotion",
        "schedule_decision": "only safe to consider after manual pass with evidence",
        "approval_artifact": "approval-request.yaml for any external action",
    }
    path.write_text("\n".join(f"{key}: {value}" for key, value in fields.items()) + "\n")


def seed_files(base, case):
    for name, content in case.get("files", {}).items():
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, (dict, list)):
            path.write_text(json.dumps(content, indent=2) + "\n")
        else:
            path.write_text(str(content))


def required_run_files(run_dir):
    names = ["checkpoint.json", "source-freeze.md", "output-packet.md", "blockers.md", "approval-request.yaml"]
    return all((run_dir / name).exists() for name in names)


def run_one(case, root):
    work = root / case["id"]
    work.mkdir(parents=True)
    seed_files(work, case)
    spec_path = work / "spec.md"
    write_spec(spec_path, case)
    init = init_checkpoint(spec_path, work / ".loop-kit" / case["id"], cwd=work)
    run_dir = Path(init["run_dir"])
    verifier_results = run_verifiers(case.get("verifiers", []), base_dir=work)
    all_verifiers_pass = all(item["passed"] for item in verifier_results) if verifier_results else False
    expected_state = case["expected_terminal_state"]
    close_error = None
    try:
        if expected_state == "no_op":
            close_checkpoint(run_dir, "no_op", no_op_reason=case.get("no_op_reason", "No fixture records"))
        elif expected_state == "manual_pass":
            close_checkpoint(
                run_dir,
                "manual_pass",
                evidence=case.get("evidence", ["fixture-evidence"]),
                verifier_results=verifier_results,
                actions=case.get("actions", ["read local fixture", "write output packet"]),
                approval_artifact=case.get("approval_artifact"),
                review_gate_passed=case.get("review_gate_passed", False),
            )
        else:
            if all_verifiers_pass:
                close_checkpoint(run_dir, expected_state, evidence=case.get("evidence", ["fixture-evidence"]), verifier_results=verifier_results)
            else:
                close_checkpoint(run_dir, expected_state)
    except ValueError as exc:
        close_error = str(exc)
        if expected_state not in {"fix_then_rerun", "approval_required", "failed_verification", "blocked"}:
            raise
        close_checkpoint(run_dir, expected_state)

    checkpoint = json.loads((run_dir / "checkpoint.json").read_text())
    output_packet = (run_dir / "output-packet.md").read_text()
    return {
        "run_dir": str(run_dir),
        "checkpoint": checkpoint,
        "verifier_results": verifier_results,
        "files_complete": required_run_files(run_dir),
        "output_complete": "- status: pending" not in output_packet,
        "close_error": close_error,
    }


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    idempotent = 0
    manual_false_passes = 0
    with tempfile.TemporaryDirectory(prefix="loop-kit-v2-") as tmp:
        root = Path(tmp)
        for case in cases:
            first = run_one(case, root / "first")
            second = run_one(case, root / "second")
            if first["checkpoint"]["terminal_state"] == second["checkpoint"]["terminal_state"]:
                idempotent += 1
            checkpoint = first["checkpoint"]
            if not first["files_complete"]:
                failures.append(f"{case['id']}: missing checkpoint artifact")
            if not first["output_complete"]:
                failures.append(f"{case['id']}: output packet remained pending")
            if checkpoint["terminal_state"] != case["expected_terminal_state"]:
                failures.append(f"{case['id']}: expected {case['expected_terminal_state']}, got {checkpoint['terminal_state']}")
            if case["expected_terminal_state"] == "manual_pass":
                if not checkpoint["evidence"] or not checkpoint["verifier_results"]:
                    manual_false_passes += 1
                if not all(item.get("passed") for item in checkpoint["verifier_results"]):
                    manual_false_passes += 1
            if case.get("expect_no_external_side_effects") and checkpoint["approval_required"]:
                failures.append(f"{case['id']}: unexpected external side effect approval requirement")
        verifier_types = set(REGISTRY)
        if len(verifier_types) < 7:
            failures.append(f"fewer than 7 verifier types: {sorted(verifier_types)}")
        for verifier_type in verifier_types:
            seen_pass = False
            seen_fail = False
            for case in cases:
                for expected in case.get("verifier_expectations", []):
                    if expected["type"] == verifier_type:
                        seen_pass = seen_pass or expected["passed"]
                        seen_fail = seen_fail or not expected["passed"]
            if not (seen_pass and seen_fail):
                failures.append(f"{verifier_type}: missing pass/fail fixture expectation")
        idempotence = idempotent / len(cases)
        if len(cases) < 5:
            failures.append(f"case count below 5: {len(cases)}")
        if idempotence < 0.95:
            failures.append(f"rerun idempotence below 95%: {idempotence:.1%}")
        if manual_false_passes:
            failures.append(f"false manual_pass closes: {manual_false_passes}")
    return {"total": len(cases), "idempotence": idempotence, "failures": failures}


if __name__ == "__main__":
    result = run()
    print(f"audit_operator_runtime_cases: {result['total'] - len(result['failures'])}/{result['total']} passed; idempotence={result['idempotence']:.1%}")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
