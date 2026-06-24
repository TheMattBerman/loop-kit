import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "scripts"))

import loop_diagnose


def test_eight_advanced_golden_examples_have_concrete_diagnosis():
    cases = json.loads((ROOT / "golden" / "advanced_cases.json").read_text())
    assert len(cases) >= 8
    for case in cases:
        result = loop_diagnose.diagnose(case["spec"])
        for field in case.get("expected_missing", []):
            assert field in result["missing_fields"], (case["id"], field, result)
        for field in case.get("expected_vague", []):
            assert field in result["vague_fields"], (case["id"], field, result)
        assert result["improvements"], case["id"]
        assert result["patches"], case["id"]
        patch_fields = {item["field"] for item in result["patches"]}
        for field in case.get("expected_missing", []) + case.get("expected_vague", []):
            assert field in patch_fields, (case["id"], field, result)
        for patch in result["patches"]:
            assert patch["replace_with"].startswith(f"{patch['field']}:"), (case["id"], patch)
