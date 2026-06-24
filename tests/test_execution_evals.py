# tests/test_execution_evals.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "shared" / "scripts"))
import design_judge as dj
def test_execution_eval_weak_design_is_rejected():
    weak = "done_criteria: keep improving until good\nverification_method: \nsource_of_truth: \napproval_boundary: "
    assert dj.judge_markdown(weak)["verdict"] == "FAIL"
def test_execution_eval_strong_design_accepted():
    strong = ("done_criteria: every item has a cited verdict\n"
              "verification_method: script asserts each claim maps to a source\n"
              "source_of_truth: the draft file\n"
              "approval_boundary: no publish without human approval")
    assert dj.judge_markdown(strong)["verdict"] == "PASS"
