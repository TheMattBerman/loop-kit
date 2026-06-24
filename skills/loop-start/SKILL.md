---
name: loop-start
description: >
  The plain-language front door for getting AI to do a recurring job for you, with
  zero jargon and no setup knowledge required. Use when a non-technical person asks:
  "I want AI to do X for me", "help me automate X", "get AI to handle X every day",
  "set up AI to do X for me", "can AI do X so I do not have to?", or "I do not know
  what a loop is but I want Y to happen on its own." Default starting point for any
  beginner who describes a goal in everyday words. Do NOT use when the user already
  speaks in design terms and wants to spec or map a loop ("design a loop for X", "turn
  this workflow into a loop") -- route that to loop-builder. Do NOT use when the user
  wants to audit, critique, or triage an existing loop ("is this loop safe?", "audit
  this spec") -- route that to loop-doctor.
metadata:
  openclaw:
    emoji: "🌱"
    user-invocable: true
    requires:
      bins: ["python3"]
      env: []
---

# Loop Start

A loop is just AI doing a job for you on repeat, without you holding its hand each time.

You do not need to know any of the inside words. Describe the job in plain English and
this skill sets it up safely, explaining everything as it goes.

## First, Offer the Depth Choice

Ask this before anything else, then default to quick:

```text
Want the quick version (I ask only what I need), or want me to walk you through it
and explain as we go?
```

## Quick Path (default)

1. Take the user's goal exactly as they said it.
2. Ask at most two plain safety follow-ups, and ONLY when the answer is missing:
   - "For one run, what would finished look like to you?"
   - "Should it ever send, post, publish, delete, or spend anything without asking
     you first?"
3. Deliver the beginner output (see below). Keep it short.

## Guided Path (deep)

Ask one plain question at a time, teaching briefly after each answer:

1. What is the job you want done?
2. How often should it happen?
3. Where does it get its information?
4. What does finished look like for one run?
5. What is it never allowed to do without checking with you first?

Then deliver the beginner output, and only here you may also show the spec if asked.

## Under the Hood (never shown to the user)

Classify the job:

```bash
python3 shared/scripts/loop_onboard.py "<the user's goal in their own words>"
```

Gate an assembled job before promising it will run:

```bash
python3 shared/scripts/validate_spec.py spec.md
python3 shared/scripts/checkpoint_run.py preflight --spec spec.md
```

Translate every result into plain words BEFORE showing anything. Use
`shared/scripts/plain_language.py` (the `plainify` function) as the single source of
truth for wording. Never show the user any inside code or label: no risk codes, no
maturity codes, no inside job-type names, and no raw verdict labels. If you are about
to type one of those, run it through plain language first.

## Beginner Output Contract

Give this back in plain words (no spec block unless the user chose the deep path and
asks for it):

1. **Here is what your loop will do.** One line, plain.
2. **On its own vs always checks with you.** Two short lists: what it handles by
   itself, and what it always runs past you first.
3. **The runnable thing.** Either a copy-paste prompt they can drop into Claude or
   Codex, or a single command to run.
4. **Try it once like this, and watch for X.** One concrete first run plus the one
   thing to keep an eye on.

Include this sentence exactly when the job is ready for a first supervised pass:

```text
I will run the first version safely, with checkpoints.
```

Then either create the first-run packet with `checkpoint_run.py init` and run only
local/read-only supported steps in the current session, or ask only for the specific
missing source, access, judgment, approval, or verification input. Ask no more than
three questions.

## Safety Trust Layer

If the gate does not pass, or a danger flag fires, do NOT show the user a raw verdict
label. Explain plainly why this job is safer with a person in the driver's seat, then
offer the safer version.

Common plain-language saves:

- It is not yet clear what finished means, so pin that down together first.
- It could send, post, publish, delete, or spend, so make it draft and wait for your
  approval instead of acting on its own.
- It could pile up more for you to review than you can keep up with, so cap how much
  it does per run.

The default safe rewrite is almost always: have it prepare the work and wait for your
yes, rather than act on its own.

External actions always stay behind approval. Sending, posting, publishing, deploying,
merging, deleting, spending, billing, or customer-facing updates require an approval
artifact before the first run can proceed.

## Hand-Off

When the job is clear and clears the gate, produce the actual runnable result through
the loop-builder design flow, then narrate it back to the user in plain words using
the beginner output contract above. The user only ever sees the plain version.
