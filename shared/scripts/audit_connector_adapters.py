#!/usr/bin/env python3
"""Audit V3-A connector adapter contract, snapshots, evidence, and fake ledgers."""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from checkpoints import close_checkpoint, init_checkpoint
from connectors import ADAPTERS, make_adapter
from evidence_packets import read_evidence, validate_evidence
from fake_providers import FakeProvider

CASES = ROOT / "golden" / "connector_adapter_cases.json"


def write_spec(path, name):
    path.write_text(
        "\n".join(
            [
                f"name: {name}",
                "source_of_truth: connector fixture",
                "done_criteria: snapshot and evidence are written",
                "verification_method: source snapshot and evidence JSONL checks pass",
                "approval_boundary: no external actions",
                "hard_stops: stop after one connector fixture",
                "no_op_condition: no source items",
                "output_packet: output-packet.md cites evidence ids",
                "first_manual_dry_run: required",
                "state_location: none",
                "",
            ]
        )
    )


def seed_source(base, case):
    source_ref = base / case["source_ref"]
    if case["adapter"] == "local_file":
        source_ref.parent.mkdir(parents=True, exist_ok=True)
        source_ref.write_text(case.get("content", "fixture content\n"))
    return str(source_ref if case["adapter"] in {"local_file", "local_repo"} else case["source_ref"])


def run_case(case, root):
    work = root / case["id"]
    work.mkdir(parents=True)
    if case["adapter"] == "local_repo":
        source_ref = str(ROOT)
    else:
        source_ref = seed_source(work, case)
    provider_root = work / "ledgers"
    adapter = make_adapter(case["adapter"], provider_root=provider_root, auth_available=case.get("auth_available", False))
    manifest = adapter.manifest()
    missing_manifest = [
        field
        for field in [
            "name",
            "version",
            "mode",
            "source_types",
            "allowed_actions",
            "draft_allowed_actions",
            "approval_required_actions",
            "forbidden_actions",
            "auth_required",
            "missing_auth_behavior",
            "snapshot_method",
            "evidence_method",
            "source_trust",
            "prompt_injection_policy",
            "side_effect_ledger_path",
        ]
        if field not in manifest
    ]
    spec = work / "spec.md"
    write_spec(spec, case["id"])
    init = init_checkpoint(spec, work / ".loop-kit" / case["id"], cwd=ROOT)
    run_dir = Path(init["run_dir"])
    result = adapter.freeze_source(source_ref, run_dir=run_dir)
    if case.get("expect_blocked"):
        return {"manifest_missing": missing_manifest, "blocked": result["status"] == "blocked", "reason": result.get("blocker"), "ledger": FakeProvider(provider_root).forbidden_side_effects()}
    snapshot = result["snapshot"]
    read = adapter.read(snapshot, run_dir=run_dir)
    evidence = read["evidence"]
    terminal_state = case.get("terminal_state", "manual_pass")
    if terminal_state == "no_op":
        close_checkpoint(
            run_dir,
            terminal_state,
            evidence=[snapshot["snapshot_id"], evidence["evidence_id"]],
            verifier_results=[{"type": "connector_snapshot", "passed": True}],
            no_op_reason="No connector source items required action",
        )
    else:
        close_checkpoint(
            run_dir,
            terminal_state,
            evidence=[snapshot["snapshot_id"], evidence["evidence_id"]],
            verifier_results=[{"type": "connector_snapshot", "passed": True}],
        )
    output_packet = (run_dir / "output-packet.md").read_text()
    return {
        "manifest_missing": missing_manifest,
        "blocked": False,
        "snapshot_exists": (run_dir / "source-snapshot.json").exists(),
        "evidence_exists": (run_dir / "evidence.jsonl").exists(),
        "evidence_valid": validate_evidence(evidence)["valid"],
        "evidence_records": read_evidence(run_dir / "evidence.jsonl"),
        "output_cites_evidence": evidence["evidence_id"] in output_packet and snapshot["snapshot_id"] in output_packet,
        "snapshot_id": snapshot["snapshot_id"],
        "evidence_id": evidence["evidence_id"],
        "terminal_state": json.loads((run_dir / "checkpoint.json").read_text())["terminal_state"],
        "required_files": all((run_dir / name).exists() for name in ["checkpoint.json", "source-freeze.md", "output-packet.md", "blockers.md", "approval-request.yaml", "source-snapshot.json", "evidence.jsonl"]),
        "ledger": FakeProvider(provider_root).forbidden_side_effects(),
    }


def run():
    cases = json.loads(CASES.read_text())
    failures = []
    adapter_classes = {case["adapter"] for case in cases}
    read_ok = 0
    nonhappy_ok = 0
    with tempfile.TemporaryDirectory(prefix="loop-kit-v3a-") as tmp:
        root = Path(tmp)
        for case in cases:
            result = run_case(case, root)
            if result["manifest_missing"]:
                failures.append(f"{case['id']}: manifest missing {result['manifest_missing']}")
            if result["ledger"]:
                failures.append(f"{case['id']}: forbidden side-effect ledger entries {result['ledger']}")
            if case.get("expect_blocked"):
                if not result["blocked"] or case.get("missing_access") not in str(result.get("reason")):
                    failures.append(f"{case['id']}: expected blocked missing access {case.get('missing_access')}, got {result}")
                continue
            if not result["snapshot_exists"] or not result["evidence_exists"]:
                failures.append(f"{case['id']}: missing snapshot or evidence artifact")
            if not result["evidence_valid"]:
                failures.append(f"{case['id']}: invalid evidence record")
            if not result["output_cites_evidence"]:
                failures.append(f"{case['id']}: output packet does not cite snapshot/evidence ids")
            if not result["required_files"]:
                failures.append(f"{case['id']}: missing required dogfood/checkpoint artifact")
            if case["adapter"] in {"local_file", "local_repo", "fake_url"}:
                read_ok += 1
            if result["terminal_state"] in {"no_op", "blocked", "fix_then_rerun"}:
                nonhappy_ok += 1
    if len(adapter_classes) < 5:
        failures.append(f"fewer than 5 connector classes tested: {sorted(adapter_classes)}")
    if read_ok < 3:
        failures.append(f"fewer than 3 read-only/draft-only adapters passed snapshot/evidence: {read_ok}")
    if nonhappy_ok < 3:
        failures.append(f"fewer than 3 non-happy dogfood-style runs closed correctly: {nonhappy_ok}")
    return {"total": len(cases), "classes": len(adapter_classes), "failures": failures}


if __name__ == "__main__":
    result = run()
    print(f"audit_connector_adapters: {result['total'] - len(result['failures'])}/{result['total']} passed; classes={result['classes']}")
    for failure in result["failures"]:
        print(f"  FAIL: {failure}")
    raise SystemExit(1 if result["failures"] else 0)
