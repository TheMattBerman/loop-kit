# Example Loop Packets

These are compact examples of the standard the skill should hit. Adapt them; do not copy blindly.

## Example: Recent Feedback Sweep

```markdown
## Loop Map
- Working name: Recent Feedback Sweep
- User goal: Turn repeated corrections into better future agent behavior.
- Recurring job: Review recent feedback, rejected outputs, and user corrections; propose durable skill/template/checker changes.
- Trigger: On demand after a rough week, or monthly.
- Source of truth: Current conversation summaries, edited skill files, accepted/rejected outputs, user corrections.
- Output packet: Patterns found, proposed changes, files to patch, validation plan.
- Done means: Each repeated correction is either converted into a concrete change or explicitly rejected as one-off noise.
- How it checks: Diffs validate, examples still pass, and the change maps to actual correction evidence.
- Human decision: Operator approves which behavior changes should become permanent.
- Risk level: R2 artifact changes.
- Recommended archetype: Compound Learning Loop.
- Maturity target: L2 stateful manual loop.
- Best first version: Manual run over the last 5-10 corrections.
```

## Example: Content Review Queue

```markdown
## Loop Map
- Working name: Content Review Queue
- User goal: Prevent weak drafts from publishing without source proof.
- Recurring job: Inspect draft pages and return approve/fix/reject packets.
- Trigger: When drafts enter review or on a fixed cadence.
- Source of truth: Draft files, source notes, keyword plan, live site constraints.
- Output packet: Verdict, source-proof gaps, rewrite notes, publish decision.
- Done means: Every reviewed draft has a decision and cited evidence.
- How it checks: Drafts are compared to source notes and public eligibility rules.
- Human decision: Operator decides publish, rewrite, or hold.
- Risk level: R1 read-only review unless the loop edits drafts.
- Recommended archetype: Review Queue Loop.
- Maturity target: L1 manual loop first.
- Best first version: Review up to 5 drafts, no publishing.
```

## Example: Customer AI Deployment Loop

```markdown
## Loop Map
- Working name: Customer AI Deployment Loop
- User goal: Move one client AI workflow from idea to usable rollout without overbuilding.
- Recurring job: Select one workflow, gather real inputs, run a dry test, capture evidence, and recommend the next rollout step.
- Trigger: New client workflow candidate or weekly implementation review.
- Source of truth: Client context, call notes, workflow owner notes, sample inputs, existing tools.
- Output packet: Priority, dry-run proof, risks, owner decision, rollout/stall recommendation.
- Done means: One workflow has a tested sample run and clear go/no-go/stage-next decision.
- How it checks: Real sample input was used, output was reviewed by owner criteria, blockers are explicit.
- Human decision: Operator or client owner approves next stage.
- Risk level: R3 customer ops.
- Recommended archetype: Customer Deployment Loop.
- Maturity target: L2 before any schedule.
- Best first version: One workflow, one dry run, no live client-facing automation.
```
