import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from checkpoints import close_checkpoint, init_checkpoint
from verifiers import run_verifiers


def _spec(tmp_path, state=False):
    path = tmp_path / "spec.md"
    path.write_text(
        "\n".join(
            [
                "name: fixture read-only loop",
                "source_of_truth: input.json",
                "done_criteria: output.json has status equal to reviewed",
                "verification_method: JSON field check for status",
                "approval_boundary: no external actions",
                "hard_stops: stop after one input file",
                "no_op_condition: input file has no records",
                "output_packet: output-packet.md with evidence id",
                "first_manual_dry_run: required before repeat",
                f"state_location: {'.loop-kit/STATE.md' if state else 'none'}",
                "",
            ]
        )
    )
    return path


def _expanded_spec(tmp_path):
    path = tmp_path / "expanded-spec.md"
    path.write_text(
        "\n".join(
            [
                "name: customer-facing review loop",
                "risk: R4",
                "maturity: L4",
                "scope: customer production",
                "source_of_truth: draft queue",
                "done_criteria: every draft has approve fix or reject verdict",
                "verification_method: JSON field check for verdict",
                "approval_boundary: publish requires approval",
                "hard_stops: stop after three drafts or missing approval",
                "no_op_condition: no drafts in queue",
                "output_packet: output-packet.md with verdicts and evidence",
                "first_manual_dry_run: completed before repeat",
                "tools_and_permissions: read queue and write local packet only",
                "state_location: .loop-kit/STATE.md",
                "run_artifacts: checkpoint.json source-freeze.md output-packet.md",
                "maker_checker_split: maker and checker must be different",
                "schedule_decision: safe to consider only after manual pass",
                "approval_artifact: approval-request.yaml",
                "",
            ]
        )
    )
    return path


def test_init_creates_checkpoint_files_and_state_only_when_required(tmp_path):
    spec = _spec(tmp_path, state=False)
    out = tmp_path / "loop"
    result = init_checkpoint(spec, out, cwd=ROOT)
    run_dir = pathlib.Path(result["run_dir"])

    assert (out / "spec.md").exists()
    assert not (out / "STATE.md").exists()
    for name in ["checkpoint.json", "source-freeze.md", "output-packet.md", "blockers.md", "approval-request.yaml"]:
        assert (run_dir / name).exists()

    stateful = tmp_path / "stateful"
    init_checkpoint(_spec(tmp_path, state=True), stateful, cwd=ROOT)
    assert (stateful / "STATE.md").exists()


def test_close_blocks_manual_pass_without_evidence(tmp_path):
    result = init_checkpoint(_spec(tmp_path), tmp_path / "loop", cwd=ROOT)
    try:
        close_checkpoint(result["run_dir"], "manual_pass")
    except ValueError as exc:
        assert "manual_pass requires evidence" in str(exc)
    else:
        raise AssertionError("manual_pass without evidence should fail")


def test_close_accepts_no_op_with_reason(tmp_path):
    result = init_checkpoint(_spec(tmp_path), tmp_path / "loop", cwd=ROOT)
    closed = close_checkpoint(result["run_dir"], "no_op", no_op_reason="No input rows")
    assert closed["terminal_state"] == "no_op"
    assert closed["ended_at"]


def test_local_read_only_fixture_loop_init_verify_close(tmp_path):
    spec = _spec(tmp_path)
    source = tmp_path / "input.json"
    output = tmp_path / "output.json"
    source.write_text(json.dumps({"status": "ready"}))
    output.write_text(json.dumps({"status": "reviewed"}))

    result = init_checkpoint(spec, tmp_path / "loop", cwd=ROOT)
    verifier_results = run_verifiers(
        [
            {"type": "file_exists", "path": str(output)},
            {"type": "json_field", "path": str(output), "field": "status", "equals": "reviewed"},
            {"type": "command_exit", "command": [sys.executable, "-c", "raise SystemExit(0)"]},
        ]
    )
    assert all(item["passed"] for item in verifier_results)

    closed = close_checkpoint(
        result["run_dir"],
        "manual_pass",
        evidence=["fixture-output-json"],
        verifier_results=verifier_results,
        actions=["read input.json", "write output packet"],
    )
    assert closed["terminal_state"] == "manual_pass"
    assert closed["schedule_recommendation"] == "safe_to_consider_scheduling"
    output_packet = (pathlib.Path(result["run_dir"]) / "output-packet.md").read_text()
    assert "- status: manual_pass" in output_packet
    assert "fixture-output-json" in output_packet
    assert "- status: pending" not in output_packet


def test_spec_derived_review_gate_blocks_graduation_close(tmp_path):
    result = init_checkpoint(_expanded_spec(tmp_path), tmp_path / "loop", cwd=ROOT)

    try:
        close_checkpoint(
            result["run_dir"],
            "manual_pass",
            evidence=["ev-1"],
            verifier_results=[{"type": "json_field", "passed": True}],
        )
    except ValueError as exc:
        assert "schedule promotion requires review gate" in str(exc)
        assert "schedule promotion requires approval artifact" in str(exc)
    else:
        raise AssertionError("expanded spec should require review gate and approval artifact")

    try:
        close_checkpoint(
            result["run_dir"],
            "manual_pass",
            evidence=["ev-1"],
            verifier_results=[{"type": "json_field", "passed": True}],
            review_gate_passed=True,
        )
    except ValueError as exc:
        assert "schedule promotion requires approval artifact" in str(exc)
    else:
        raise AssertionError("expanded spec should require approval artifact")

    closed = close_checkpoint(
        result["run_dir"],
        "manual_pass",
        evidence=["ev-1"],
        verifier_results=[{"type": "json_field", "passed": True}],
        approval_artifact="approval-request.yaml",
        review_gate_passed=True,
    )
    assert closed["review_gate_required"] is True
    assert closed["review_gate_passed"] is True
    assert closed["approval_artifact_required"] is True
    assert closed["schedule_recommendation"] == "safe_to_consider_scheduling"


def test_checkpoint_cli_init_and_close(tmp_path):
    spec = _spec(tmp_path)
    out = tmp_path / "cli-loop"
    init = subprocess.run(
        [sys.executable, "shared/scripts/checkpoint_run.py", "init", "--spec", str(spec), "--out", str(out)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert init.returncode == 0, init.stderr
    run_dir = json.loads(init.stdout)["run_dir"]

    bad = subprocess.run(
        [sys.executable, "shared/scripts/checkpoint_run.py", "close", "--run", run_dir, "--verdict", "manual_pass"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert bad.returncode != 0

    good = subprocess.run(
        [
            sys.executable,
            "shared/scripts/checkpoint_run.py",
            "close",
            "--run",
            run_dir,
            "--verdict",
            "manual_pass",
            "--evidence",
            "ev-1",
            "--verifier-result",
            "json_field:pass",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert good.returncode == 0, good.stderr
    output_packet = (pathlib.Path(run_dir) / "output-packet.md").read_text()
    assert "- status: manual_pass" in output_packet
    assert "ev-1" in output_packet
