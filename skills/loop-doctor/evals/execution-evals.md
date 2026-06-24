# loop-doctor Execution Evals

Each eval below lists: the input, the runnable command, and the expected output.
Run all commands from the repo root.

---

## Eval D-1: Weak spec is rejected (FAIL)

**Purpose:** Confirm the judge rejects a spec with vague done criteria and missing required fields.

**Input (pipe to stdin):**

```
done_criteria: keep improving until good
verification_method: 
source_of_truth: 
approval_boundary: 
```

**Runnable command:**

```bash
printf 'done_criteria: keep improving until good\nverification_method: \nsource_of_truth: \napproval_boundary: \n' | python3 shared/scripts/design_judge.py
```

**Expected output:**

```json
{
  "verdict": "FAIL",
  "missing": [
    "verification_method",
    "source_of_truth",
    "approval_boundary"
  ],
  "vague": [
    "done_criteria"
  ]
}
```

**Expected exit code:** 0 (the judge always exits 0; the FAIL verdict is in the JSON)

---

## Eval D-2: Strong spec passes (PASS)

**Purpose:** Confirm the judge accepts a spec where all required fields are present and non-vague.

**Input (pipe to stdin):**

```
done_criteria: every item has a cited verdict
verification_method: script asserts each claim maps to a source
source_of_truth: the draft file
approval_boundary: no publish without human approval
```

**Runnable command:**

```bash
printf 'done_criteria: every item has a cited verdict\nverification_method: script asserts each claim maps to a source\nsource_of_truth: the draft file\napproval_boundary: no publish without human approval\n' | python3 shared/scripts/design_judge.py
```

**Expected output:**

```json
{
  "verdict": "PASS",
  "missing": [],
  "vague": []
}
```

**Expected exit code:** 0

---

## Eval D-3: Golden regression suite passes

**Purpose:** Confirm the full golden-case regression suite (which loop-doctor depends on) passes.

**Runnable command:**

```bash
python3 shared/scripts/audit_kit.py
```

**Expected output:**

```
audit_kit: 4/4 passed
```

**Expected exit code:** 0

---

## Machine-checkable assertions (Python)

The following assertions are also encoded as pytest tests in `tests/test_execution_evals.py`
and run as part of the standard test suite:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "shared" / "scripts"))
import design_judge as dj

# D-1: weak spec is rejected
weak = "done_criteria: keep improving until good\nverification_method: \nsource_of_truth: \napproval_boundary: "
assert dj.judge_markdown(weak)["verdict"] == "FAIL"

# D-2: strong spec is accepted
strong = ("done_criteria: every item has a cited verdict\n"
          "verification_method: script asserts each claim maps to a source\n"
          "source_of_truth: the draft file\n"
          "approval_boundary: no publish without human approval")
assert dj.judge_markdown(strong)["verdict"] == "PASS"
```
