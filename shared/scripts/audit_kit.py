"""Regression harness: runs all golden cases against loop_onboard and design_judge.

Usage:
    python3 shared/scripts/audit_kit.py
Exits 1 if any case fails, 0 if all pass.
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
_CASES_PATH = _REPO_ROOT / "golden" / "cases.json"

sys.path.insert(0, str(_HERE))
from loop_onboard import map_loop
from design_judge import judge


def run():
    """Run all golden cases and return {passed, failed, failures}."""
    cases = json.loads(_CASES_PATH.read_text())
    passed = 0
    failed = 0
    failures = []

    for case in cases:
        case_id = case["id"]
        kind = case["kind"]

        if kind == "onboard":
            result = map_loop(case["input"])
            dump = json.dumps(result, default=str)

            ok = True
            for substring in case.get("must_include", []):
                if substring not in dump:
                    failures.append(f"{case_id}: must_include {substring!r} not found in output")
                    ok = False

            for substring in case.get("must_not_include", []):
                if substring in dump:
                    failures.append(f"{case_id}: must_not_include {substring!r} found in output")
                    ok = False

            if ok:
                passed += 1
            else:
                failed += 1

        elif kind == "judge":
            result = judge(case["spec"])
            verdict = result["verdict"]
            expected = case["expect_verdict"]
            if verdict == expected:
                passed += 1
            else:
                failures.append(
                    f"{case_id}: expected verdict {expected!r} but got {verdict!r}"
                    f" (missing={result['missing']}, vague={result['vague']})"
                )
                failed += 1

        else:
            failures.append(f"{case_id}: unknown kind {kind!r}")
            failed += 1

    return {"passed": passed, "failed": failed, "failures": failures}


if __name__ == "__main__":
    result = run()
    total = result["passed"] + result["failed"]
    print(f"audit_kit: {result['passed']}/{total} passed")
    if result["failures"]:
        for msg in result["failures"]:
            print(f"  FAIL: {msg}")
    sys.exit(1 if result["failed"] else 0)
