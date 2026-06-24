# loop-start Execution Evals

Each eval lists: the input, a runnable command, and the expected plain result.
Run all commands from the repo root. Every result a beginner sees is plain English with
no inside codes (no risk codes, no maturity codes, no inside job-type names, no raw
verdict labels).

---

## Eval S-1: Plain translation of a real goal

**Purpose:** Confirm a real goal is classified and translated into plain words with the
four beginner keys and no inside codes.

**Input:** "review my drafts before publishing"

**Runnable command:**

```bash
python3 shared/scripts/plain_language.py "review my drafts before publishing"
```

**Expected output (plain JSON, keys exactly `what_it_does`, `careful_because`, `how_it_starts`, `watch_for`):**

```json
{
  "what_it_does": "a job that reviews items and returns approve, fix, or reject",
  "careful_because": "it only reviews and flags, it does not change anything",
  "how_it_starts": "start by running it yourself a few times before automating",
  "watch_for": [
    "It could send, post, publish, delete, or spend, so it should ask you first."
  ]
}
```

**Expected exit code:** 0. No token matching a risk code, a maturity code, the inside
word for a job type, or a raw verdict label appears anywhere in the output.

---

## Eval S-2: Jargon-free contract holds (PASS)

**Purpose:** Confirm that a real classification run through the plain-language layer is
free of inside codes for a spread of beginner inputs. This is the round-trip the
integration gate keys on.

**Runnable command:**

```bash
python3 -m pytest tests/test_loop_start_contract.py -q
```

**Expected output:**

```
1 passed
```

**Expected exit code:** 0

---

## Eval S-3: Unsafe job triggers the plain trust layer

**Purpose:** Confirm a job that would act on the outside world without asking surfaces
the plain-language safety save (offer the draft-and-wait version) and never shows a raw
verdict label to the user.

**Input:** "publish my posts automatically until they look good"

**Runnable command:**

```bash
python3 shared/scripts/plain_language.py "publish my posts automatically until they look good"
```

**Expected output (note the `watch_for` save; no raw verdict label):**

```json
{
  "what_it_does": "a job AI runs for you on repeat",
  "careful_because": "it only reads and suggests, so it is low risk",
  "how_it_starts": "you can do this with a single prompt for now",
  "watch_for": [
    "It could send, post, publish, delete, or spend, so it should ask you first."
  ]
}
```

**Expected beginner-facing behavior:** the skill reads the `watch_for` save and tells
the user plainly that publishing on its own is risky, then offers the safer version:
have it prepare the posts and wait for your yes before anything goes live. The user
never sees a raw verdict label; the safe rewrite is draft-and-wait-for-approval.

**Expected exit code:** 0
