import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from review_gate import validate_review_packet


def test_same_actor_fails_for_consequential_loop():
    result = validate_review_packet(
        {
            "maker": "operator",
            "checker": "operator",
            "consequential": True,
            "evidence_refs": ["ev-1"],
            "checker_output": "ev-1 supports the packet",
        }
    )
    assert not result["passed"]
    assert "maker and checker must be different" in result["failures"]


def test_external_action_requires_second_review_packet():
    result = validate_review_packet({"maker": "a", "checker": "b", "external_action": True})
    assert not result["passed"]
    assert "second review packet required" in result["failures"]


def test_checker_output_must_reference_evidence():
    result = validate_review_packet(
        {
            "maker": "a",
            "checker": "b",
            "subjective": True,
            "evidence_refs": ["ev-2"],
            "checker_output": "Looks fine to me",
        }
    )
    assert not result["passed"]
    assert "checker output must cite an evidence ref" in result["failures"]


def test_valid_consequential_review_passes():
    result = validate_review_packet(
        {
            "maker": "a",
            "checker": "b",
            "consequential": True,
            "second_review_packet": True,
            "evidence_refs": ["ev-1"],
            "checker_output": "ev-1 confirms the verifier passed",
        }
    )
    assert result["passed"]
