import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from runtime_policy import detect_external_actions, evaluate_action, evaluate_close


def test_external_verbs_require_approval():
    for verb in ["send", "post", "publish", "deploy", "merge", "delete", "spend", "bill", "customer-facing update"]:
        result = evaluate_action([f"{verb} the result"])
        assert not result["allowed"], verb
        assert result["requires_approval"]


def test_external_action_still_gated_with_manual_pass():
    result = evaluate_close(
        "manual_pass",
        evidence=["ev-1"],
        verifier_results=[{"passed": True}],
        actions=["publish the output"],
    )
    assert not result["allowed"]
    assert "external action requires approval artifact" in result["failures"]


def test_schedule_promotion_requires_manual_pass_and_evidence():
    no_evidence = evaluate_close("manual_pass", verifier_results=[{"passed": True}])
    assert not no_evidence["allowed"]

    blocked = evaluate_close(
        "fix_then_rerun",
        evidence=["ev-1"],
        verifier_results=[{"passed": True}],
        schedule_recommendation="safe_to_consider_scheduling",
    )
    assert not blocked["allowed"]

    passed = evaluate_close("manual_pass", evidence=["ev-1"], verifier_results=[{"passed": True}])
    assert passed["allowed"]
    assert passed["schedule_recommendation"] == "safe_to_consider_scheduling"


def test_schedule_promotion_requires_review_and_approval_when_needed():
    missing_review = evaluate_close(
        "manual_pass",
        evidence=["ev-1"],
        verifier_results=[{"passed": True}],
        review_gate_required=True,
        approval_artifact_required=True,
    )
    assert not missing_review["allowed"]
    assert "schedule promotion requires review gate" in missing_review["failures"]
    assert "schedule promotion requires approval artifact" in missing_review["failures"]

    missing_approval = evaluate_close(
        "manual_pass",
        evidence=["ev-1"],
        verifier_results=[{"passed": True}],
        review_gate_required=True,
        review_gate_passed=True,
        approval_artifact_required=True,
    )
    assert not missing_approval["allowed"]
    assert "schedule promotion requires approval artifact" in missing_approval["failures"]

    passed = evaluate_close(
        "manual_pass",
        evidence=["ev-1"],
        verifier_results=[{"passed": True}],
        approval_artifact="approval-request.yaml",
        review_gate_required=True,
        review_gate_passed=True,
        approval_artifact_required=True,
    )
    assert passed["allowed"]
    assert passed["schedule_recommendation"] == "safe_to_consider_scheduling"


def test_no_op_is_valid_with_reason():
    result = evaluate_close("no_op", no_op_reason="No source rows changed")
    assert result["allowed"]
    assert result["schedule_recommendation"] == "do_not_schedule"


def test_scheduled_is_never_emitted_or_accepted():
    result = evaluate_close(
        "manual_pass",
        evidence=["ev-1"],
        verifier_results=[{"passed": True}],
        schedule_recommendation="scheduled",
    )
    assert not result["allowed"]
    assert result["schedule_recommendation"] != "scheduled"


def test_detect_external_actions():
    assert detect_external_actions(["read files", "customer-facing update"]) == ["customer-facing update"]
