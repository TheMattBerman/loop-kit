# tests/test_audit_kit.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "shared" / "scripts"))
import audit_kit
def test_golden_cases_all_pass():
    out = audit_kit.run()
    assert out["failed"] == 0, out["failures"]
    assert out["passed"] >= 4
