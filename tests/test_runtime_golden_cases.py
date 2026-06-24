import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "scripts"))

import audit_runtime_cases


def test_runtime_golden_cases_pass():
    result = audit_runtime_cases.run()
    assert result["failed"] == 0, result["failures"]
