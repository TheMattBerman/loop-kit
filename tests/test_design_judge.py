import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "shared" / "scripts"))
import design_judge as dj

STRONG = {
    "done_criteria": "every draft has a verdict, cited source proof, and a missing-proof list",
    "verification_method": "script asserts each claim maps to a source line; fails if any unmapped",
    "source_of_truth": "the draft file plus the keyword brief",
    "approval_boundary": "no publishing or indexing without human approval",
}

def test_strong_spec_passes():
    out = dj.judge(STRONG)
    assert out["verdict"] == "PASS", out

def test_missing_field_fails_closed():
    weak = dict(STRONG); del weak["done_criteria"]
    out = dj.judge(weak)
    assert out["verdict"] == "FAIL"
    assert "done_criteria" in out["missing"]

def test_vague_done_fails():
    weak = dict(STRONG); weak["done_criteria"] = "keep improving until it is good"
    out = dj.judge(weak)
    assert out["verdict"] == "FAIL"
    assert "done_criteria" in out["vague"]
