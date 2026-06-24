---
name: loop-builder
description: >
  Design, map, and operationalize AI agent loops from scratch. Use when the user asks:
  "turn this workflow into a loop", "design a loop for X", "build me a goal routine",
  "help me spec a recurring automation", "create a recurring agent", "map this repeating
  job", or "what would this look like as a loop?" Do NOT use when the user wants to
  audit, critique, or triage an existing loop spec (route that to loop-doctor instead).
metadata:
  openclaw:
    emoji: "🔧"
    user-invocable: true
    requires:
      bins: ["python3"]
      env: []
---

# Loop Builder

Describe a recurring workflow or agent idea and get a mapped loop, a runnable
dry-run prompt, and the smallest safe operating spec.

Core test before building anything:

```text
What does done mean, and how will the agent check?
```

If that cannot be answered concretely, produce a prompt or checklist instead of a loop.

## Modes

- **Map**: rough idea in, loop map + 1-3 sharp questions out.
- **Spec**: answers in, minimum viable or expanded spec out.
- **Dry run**: spec in, copy-paste launcher + first-run checklist out.
- **Operationalize**: add state file, graduation decision, rollback rules, reviewer gate.

## Start Here

When the user has not provided a clean loop spec, onboard the idea first:

```bash
python3 shared/scripts/loop_onboard.py "<rough workflow, pain, or goal>"
```

Ask at most 3 follow-up questions -- only for missing done criteria, source access,
approval boundary, or whether this is a loop at all.

To find matching patterns from the loop library:

```bash
python3 shared/scripts/select_loop_patterns.py "<loop job description>"
```

Use results as inspiration; adapt to the user's real source and approval constraints.

## Onboarding Output

For rough ideas, produce this before the full spec:

```markdown
## Loop Map
- Working name: / User goal: / Recurring job: / Trigger: / Source of truth:
- Output packet: / Done means: / How it checks: / Human decision:
- Risk level: / Recommended archetype: / Best first version:

## Missing Answers (up to 3)

## Recommendation
Prompt first / manual loop / repeat-ready manual loop / do not build yet: <reason>
```

## Forced Fields by Risk

**Minimum viable spec -- L1-L2 loops (internal, read-only, no external actions):**

```yaml
archetype:
trigger:
source_of_truth:
done_criteria:
verification_method:
hard_stops:
output_packet:
approval_boundary:
no_op_condition:
first_manual_dry_run:
```

**Expanded spec -- L3-L4 or any loop with customer, production, or external-action scope:**

Add to the minimum viable set: `catalog_pattern`, `maturity`, `inputs`,
`tools_and_permissions`, `state_location`, `run_artifacts`, `steps`,
`maker_checker_split`, `stop_conditions`, `risks`, `rollback_or_reversal`,
`schedule_decision`, `approval_artifact`.

## Archetypes and Reusable Mechanics

Full patterns in `shared/references/archetype-playbook.md`. One line each:

- Decision Queue: ranks messy open work into named choices.
- Review Queue: approve/fix/reject verdict packets for drafts or assets.
- Verification: iterates toward a measurable, machine-checkable bar.
- Operating: recurring repo/product/client ops with human approval gates.
- Customer Deployment: one client workflow, idea to staged rollout evidence.
- Build Promotion: converts shipped work into proof, caveats, and promo options.
- Compound Learning: repeated corrections become skills, templates, or gates.
- Adversarial Review: independent critic checks a plan before commitment.

Reusable mechanics (add only what the risk requires): source freeze, state ledger,
maker/checker split, no-op terminal, bounded pass, evidence packet, approval gate,
regression capture, dry-run first, downgrade rule.

## The Handoff Contract (Loop Builder + Loop Doctor)

Either skill can run standalone. Recommended path: run `loop-doctor` first, then
bring the verdict here to produce the full design.

**Verdict routing:**

| loop-doctor verdict | loop-builder action |
|---|---|
| `go` | Produce full spec and dry-run launcher; include STATE.md skeleton only when recurrence memory, queue, or trend tracking is needed. |
| `fix-then-go` | Surface ranked fixes first; build only after fixes are confirmed. |
| `downgrade-to-prompt` | Decline the build; return a single-use prompt or checklist. |
| `not-a-loop` | Decline the build; explain why; return the better artifact. |

When the user skips loop-doctor, apply the same fail-closed test internally:
if done/check/source is weak, downgrade and say so.

## Pointers to Loop Composition IP

Full worked examples in `shared/references/loop-composition.md`. Do not duplicate.

- **Loop-stack / packet-handoff model**: one loop per stage, typed output packet,
  no back-reads across stages. Use when the workflow spans more than two bounded jobs.
- **Claim-ledger gate**: per-claim source binding before any artifact goes public;
  required for numerical, client, or high-risk-vertical claims.
- **Deterministic-hygiene vs. semantic-editorial two-tier gate**: Tier 1 automated
  hygiene runs first; Tier 2 rendered/human editorial review runs only after Tier 1
  passes. Neither tier substitutes for the other.

## Required Output for a Finished Design

```markdown
## Loop Map
<Job, trigger, source, output, done/check, human decision, best first version.>

## Loop Spec
<Minimum viable or expanded YAML block per risk level.>

## Done and Verification
Done means: / How it checks: / Evidence required: / Maker/checker split:

## Hard Stops
Max time / items / attempts / spend: / Blocked condition:

## Human Boundary
Allowed: / Requires approval: / Forbidden:

## First Manual Dry Run
<Steps to run once before scheduling.>

## First Run Checkpoint
- Source freeze:
- Allowed actions:
- Forbidden actions:
- Hard stops:
- Required evidence:
- Run action:
- Terminal states:
- Schedule graduation rule:

## First Run Result
- Terminal state:
- Evidence:
- Verifier results:
- Blockers:
- Next decision:
- Schedule recommendation:

## Callable Prompt
<Copy-paste prompt for Codex or Claude.>

## STATE.md Skeleton
<Only when the loop needs recurrence memory, queue tracking, or trend data.>
```

Use the checkpoint runtime when a spec is ready:

```bash
python3 shared/scripts/validate_spec.py spec.md
python3 shared/scripts/checkpoint_run.py init --spec spec.md --out .loop-kit/<loop-slug>
python3 shared/scripts/checkpoint_run.py close --run .loop-kit/<loop-slug>/runs/<run-id> --verdict manual_pass --evidence <id> --verifier-result <type>:pass
```

Never create background operation or a recurring schedule. A clean first run can only
return `safe_to_consider_scheduling`.

## References

- `shared/references/loop-onboarding.md`: question bank and risk ladder.
- `shared/references/archetype-playbook.md`: archetype inputs, gates, outputs.
- `shared/references/loop-spec-template.md`: spec templates (both tiers).
- `shared/references/loop-launcher-template.md`: first-run launcher format.
- `shared/references/example-loop-packets.md`: good and bad loop map examples.
- `shared/references/loop-red-flags.md`: failure modes and downgrade rules.
- `shared/references/loop-library-analysis.md`: maturity taxonomy and pitfalls.
- `shared/references/loop-composition.md`: loop-stack, claim-ledger, two-tier gate.
