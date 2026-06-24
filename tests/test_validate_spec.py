import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from spec_schema import validate_spec


VALID_MINIMUM = {
    "source_of_truth": "fixtures/input.json",
    "done_criteria": "Every input item has a reviewed boolean field",
    "verification_method": "JSON field check for reviewed",
    "approval_boundary": "No external actions are allowed",
    "hard_stops": "Stop after 10 items or 60 seconds",
    "no_op_condition": "No input items exist",
    "output_packet": "review summary with evidence ids",
    "first_manual_dry_run": "Run once under human supervision before any repeat",
}


def test_minimum_spec_requires_checkpoint_fields():
    for field in [
        "source_of_truth",
        "done_criteria",
        "verification_method",
        "approval_boundary",
        "hard_stops",
        "no_op_condition",
        "first_manual_dry_run",
    ]:
        spec = dict(VALID_MINIMUM)
        spec.pop(field)
        result = validate_spec(spec)
        assert not result["valid"]
        assert field in result["missing"]


def test_expanded_spec_requires_runtime_fields_for_external_action():
    spec = dict(VALID_MINIMUM)
    spec["approval_boundary"] = "Publishing requires approval"
    result = validate_spec(spec)
    assert not result["valid"]
    for field in [
        "tools_and_permissions",
        "state_location",
        "run_artifacts",
        "maker_checker_split",
        "schedule_decision",
        "approval_artifact",
    ]:
        assert field in result["missing"]


def test_vague_done_and_verification_fail():
    spec = dict(VALID_MINIMUM)
    spec["done_criteria"] = "make it better"
    spec["verification_method"] = "looks good"
    result = validate_spec(spec)
    assert not result["valid"]
    assert set(result["vague"]) == {"done_criteria", "verification_method"}


def test_validate_spec_cli_exit_codes(tmp_path):
    valid = tmp_path / "valid.json"
    valid.write_text(json.dumps(VALID_MINIMUM))
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps({"done_criteria": "good"}))

    ok = subprocess.run([sys.executable, "shared/scripts/validate_spec.py", str(valid)], cwd=ROOT)
    bad = subprocess.run([sys.executable, "shared/scripts/validate_spec.py", str(invalid)], cwd=ROOT)

    assert ok.returncode == 0
    assert bad.returncode != 0
