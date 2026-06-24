---
name: loop-doctor
description: >
  Audit, critique, and triage AI agent loops to determine whether a loop is safe to run,
  worth building, or should be downgraded. Use when the user asks: "should I automate this?",
  "is this loop safe?", "why is my loop producing junk?", "audit this loop spec", "critique
  this automation", "is this a good loop?", or "review my recurring agent workflow."
  Do NOT use when the user wants to design or build a brand-new loop from a rough idea
  (route that to loop-builder instead).
metadata:
  openclaw:
    emoji: "🩺"
    user-invocable: true
    requires:
      bins: ["python3"]
      env: []
---

# Loop Doctor

**Fail-closed triage for AI agent loops.** Before a loop is scheduled or externalized,
the doctor answers one question: is this safe to run, and where will it hurt you?

## The Core Test

```text
What does done mean, and how will the agent check?
```

If neither half of that question has a concrete, machine-verifiable answer, the loop
is not ready. Downgrade it.

## How to Run the Diagnosis

**Step 1 -- onboard the loop description:**

```bash
python3 shared/scripts/loop_onboard.py "describe the loop in one or two sentences"
```

Read the output. Note danger flags, missing fields, and the recommended archetype.

**Step 2 -- judge an existing spec:**

```bash
python3 shared/scripts/validate_spec.py spec.md
```

The validator checks the full checkpoint spec: source, done, verifier, hard stops,
no-op condition, output packet, approval boundary, and first manual dry run. For
higher-risk, production, customer-facing, or external-action loops it also requires
tools/permissions, state, run artifacts, maker/checker split, schedule decision, and
approval artifact. A `FAIL` verdict means the loop must be fixed or downgraded before
it runs.

**Step 3 -- issue the VERDICT (see below).**

## VERDICT Output Contract

Every diagnosis ends with exactly one verdict and a ranked fix list.

| Verdict | Meaning |
|---|---|
| `go` | Required fields present, done/check concrete, approval boundary explicit, no Kill-On-Sight patterns. Safe to run. |
| `fix-then-go` | Fixable gaps found. Return the ranked fix list; re-run the judge after fixes. |
| `downgrade-to-prompt` | Done or check is weak, or source of truth is inaccessible. Convert to a one-off prompt or manual checklist. |
| `not-a-loop` | The job does not recur, has no checkable done state, or lacks a named source of truth. Do not build as a loop. |

### Verdict format

```markdown
## Loop Doctor Verdict: <verdict>

**Risks tripped:** <comma-separated named risks, or "none">

**Ranked fixes:**
1. <highest-priority fix>
2. ...

**Reasoning:** <one sentence>
```

## Fail-Closed Downgrade Rule

Downgrade to `downgrade-to-prompt` or `not-a-loop` when ANY of the following are true:

- `done_criteria` is empty, vague, or relies on subjective human taste
- `verification_method` has no machine-checkable step
- `source_of_truth` is unknown, inaccessible, or changes mid-run without versioning
- `approval_boundary` is absent on any loop that can send, publish, deploy, merge,
  delete, spend, or touch a customer

When in doubt, downgrade. A prompt that works beats a loop that silently fails.

## Safety-Forced Fields

These fields are non-negotiable. A missing field blocks `go` and `fix-then-go`, forcing `downgrade-to-prompt` or `not-a-loop`.

```yaml
approval_boundary:   # what the agent may NOT do without human sign-off
hard_stops:          # conditions that halt the loop immediately (time/cost/error limits)
no_op_condition:     # what counts as "nothing to do" (must be a valid terminal state)
first_manual_dry_run: # proof that one full run was completed and reviewed by a human
```

## Kill-On-Sight Anti-Patterns

Flag any of these immediately. They block `go`.

- **Vibe loop** -- "keep improving until satisfied." No rubric, no cap. Downgrade.
- **Tool-first loop** -- built around cron/subagents/MCPs before the job is mapped.
  Map the job first.
- **Fake autonomy** -- hides a human decision inside "agent decides." Name the boundary.
- **Review-debt machine** -- produces more findings than the operator can use. Cap and rank.
- **State theater** -- creates a state file when no memory, queue, or trend tracking is needed.
- **Unsafe externalization** -- send/publish/deploy/merge/delete/spend/customer-facing
  action without an explicit approval gate.
- **Self-graded taste** -- the loop approves its own subjective creative or strategy output.
  Add a checker or a human gate.

## Named Failure Modes (Key IP)

These are the failure patterns that recur across real-world agent loops.
Surface them by name in the verdict when they apply.

- **Ralph Wiggum loop** -- the loop emits a soft completion token ("done!", "looks good")
  on a half-finished job, and no check catches it. The agent signals success; the work is
  missing. Fix: require a hard, machine-verifiable done signal.

- **Comprehension debt** -- the loop produces output the operator cannot interpret fast
  enough to catch errors. Each run leaves more unread artifacts. Fix: cap batch size and
  require a human-readable summary per run.

- **Cognitive surrender** -- the operator stops reading the output because the loop
  "usually works." Errors accumulate invisibly. Fix: sample and spot-check every Nth run;
  require explicit sign-off before scheduling increases.

- **The security tax** -- skills and prompt templates become injection vectors; secrets leak
  into logs; permissions expand silently. Fix: no secrets in logs, audit permissions every
  30 days, treat skill files as attack surface.

## Headline Loop-Health Metric

> **Cost per accepted change below 50% means the loop is losing.**

Of all changes the loop proposes, what fraction does the operator actually accept?
Below 50% means the loop generates more noise than value. Target above 50%.
Track this per run and downgrade or cap the loop if the rate stays below threshold.

## Audit Checklist

Use this when critiquing an existing loop spec:

- [ ] `done_criteria` is concrete and machine-verifiable
- [ ] `verification_method` has a named check step
- [ ] `source_of_truth` is named and accessible
- [ ] `approval_boundary` is explicit for any external action
- [ ] `hard_stops` are present (time, item count, spend, or error threshold)
- [ ] `no_op_condition` is defined (the loop can exit cleanly with nothing done)
- [ ] `first_manual_dry_run` has been completed before scheduling
- [ ] No Kill-On-Sight anti-patterns detected
- [ ] Acceptance rate tracked or estimable (target above 50%)
- [ ] Maker/checker split present for any consequential or subjective output
- [ ] Strong spec validation passes (`validate_spec.py`)
- [ ] First-run checkpoint packet exists before any graduation recommendation
- [ ] Approval artifact exists when external actions are requested
- [ ] Review gate passes when maker/checker separation is required
- [ ] Schedule recommendation is blocked unless manual-pass evidence exists

Checkpoint readiness commands:

```bash
python3 shared/scripts/checkpoint_run.py preflight --spec spec.md
python3 shared/scripts/runtime_guard.py close --terminal-state manual_pass --evidence <id> --verifier-result command_exit:pass
python3 shared/scripts/review_gate.py review.json
```

## What Loop Doctor Does NOT Do

- It does not design or spec a new loop. Route that to loop-builder.
- It does not generate copy-paste launchers. Those come after a `go` verdict.
- It does not choose archetypes. It checks whether the spec is safe regardless of archetype.

## References (one-line pointers -- do not duplicate their contents)

- `shared/references/loop-red-flags.md` -- full failure-mode catalog and downgrade rules.
- `shared/references/loop-onboarding.md` -- guided question bank and risk ladder.
- `shared/references/archetype-playbook.md` -- archetype-by-archetype inputs, gates, and outputs.
- `shared/references/loop-spec-template.md` -- minimum viable and expanded spec templates.
- `shared/references/loop-launcher-template.md` -- first-run launcher after a `go` verdict.
- `shared/references/example-loop-packets.md` -- good and bad loop maps for calibration.
- `shared/references/loop-library-analysis.md` -- maturity taxonomy and common pitfalls.
- `shared/references/loop-composition.md` -- rules for combining multiple loops safely.
