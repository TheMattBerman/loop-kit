import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from verifiers import REGISTRY, run_verifier


def test_registry_has_required_deterministic_types():
    assert {
        "command_exit",
        "file_exists",
        "json_field",
        "regex_text",
        "file_diff",
        "count_threshold",
        "source_snapshot_hash",
    } <= set(REGISTRY)


def test_command_exit_pass_and_fail():
    passed = run_verifier({"type": "command_exit", "command": [sys.executable, "-c", "raise SystemExit(0)"]})
    failed = run_verifier({"type": "command_exit", "command": [sys.executable, "-c", "raise SystemExit(2)"]})
    assert passed["passed"]
    assert not failed["passed"]


def test_file_exists_pass_and_fail(tmp_path):
    path = tmp_path / "exists.txt"
    path.write_text("ok")
    assert run_verifier({"type": "file_exists", "path": str(path)})["passed"]
    assert not run_verifier({"type": "file_exists", "path": str(tmp_path / "missing.txt")})["passed"]


def test_json_field_pass_and_fail(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(json.dumps({"status": {"value": "ready"}}))
    assert run_verifier({"type": "json_field", "path": str(path), "field": "status.value", "equals": "ready"})["passed"]
    assert not run_verifier({"type": "json_field", "path": str(path), "field": "status.value", "equals": "done"})["passed"]


def test_regex_text_pass_and_fail(tmp_path):
    path = tmp_path / "packet.md"
    path.write_text("status: reviewed\n")
    assert run_verifier({"type": "regex_text", "path": str(path), "pattern": "reviewed"})["passed"]
    assert not run_verifier({"type": "regex_text", "path": str(path), "pattern": "missing"})["passed"]


def test_file_diff_pass_and_fail(tmp_path):
    before = tmp_path / "before.txt"
    after = tmp_path / "after.txt"
    same = tmp_path / "same.txt"
    before.write_text("before\n")
    after.write_text("after\n")
    same.write_text("before\n")
    assert run_verifier({"type": "file_diff", "before": str(before), "after": str(after), "expect_changed": True})["passed"]
    assert not run_verifier({"type": "file_diff", "before": str(before), "after": str(same), "expect_changed": True})["passed"]


def test_count_threshold_pass_and_fail(tmp_path):
    path = tmp_path / "rows.txt"
    path.write_text("one\ntwo\n")
    assert run_verifier({"type": "count_threshold", "path": str(path), "minimum": 2})["passed"]
    assert not run_verifier({"type": "count_threshold", "path": str(path), "minimum": 3})["passed"]


def test_source_snapshot_hash_pass_and_fail(tmp_path):
    path = tmp_path / "source.txt"
    path.write_text("source\n")
    result = run_verifier({"type": "source_snapshot_hash", "path": str(path)})
    assert result["passed"]
    assert result["evidence_id"]
    assert run_verifier({"type": "source_snapshot_hash", "path": str(path), "sha256": result["actual"]})["passed"]
    assert not run_verifier({"type": "source_snapshot_hash", "path": str(path), "sha256": "wrong"})["passed"]
