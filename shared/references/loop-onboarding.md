# Loop Onboarding

Use this when the user has a fuzzy loop idea, asks to "build a loop with me," or gives a recurring pain without a spec.

## Principle

Do not interrogate the user with a long form. Build the first map from what they already gave you, then ask only for missing answers that change the design.

Maximum questions before first draft: 3.

## The 8-Field Map

Every loop starts as these fields:

| Field | Why it matters | Good answer |
|---|---|---|
| Job | Prevents tool-first automation | "Review new content drafts for source proof and publish readiness." |
| Trigger | Proves it is a loop | "When new drafts enter review" or "Every Friday." |
| Source of truth | Prevents hallucinated work | "Draft files, source docs, analytics export." |
| Output packet | Makes the result usable | "Approve / fix / reject packet with evidence." |
| Done means | Defines the target | "Every draft has source proof, risk flags, and a decision." |
| How it checks | Makes it engineerable | "Checklist plus links/screenshots/source excerpts." |
| Human decision | Keeps agency with the operator | "Operator approves publish or rewrite." |
| Risk | Decides ceremony level | "Read-only review" vs "customer-facing change." |

## Question Ladder

Ask questions in this order. Stop once you can produce a useful first map.

1. **Outcome**: "What should the loop hand you at the end: a decision queue, review packet, fixed artifact, report, or executed change?"
2. **Source**: "What should it inspect as truth: files, repo, TODOs, Drive, CRM, analytics, browser, emails, client docs, or another system?"
3. **Done/check**: "What would make you say this run passed?"
4. **Boundary**: "What can it do without approval, and what must it never do without approval?"
5. **Cadence**: "Should it run on demand, on a schedule, on a state change, or only after a manual kickoff?"
6. **State**: "Does it need to remember previous runs, open items, scores, exceptions, or lessons?"
7. **Reviewer**: "Should a second agent/person check the output before action?"
8. **Failure**: "What should it do when there is nothing to act on or it cannot verify the source?"

## Risk Ladder

Use risk to choose how much structure to force:

| Risk | Examples | Required structure |
|---|---|---|
| R0 prompt/checklist | One-off strategy, brainstorm, rewrite | No loop; give a prompt/checklist |
| R1 read-only review | Content review, TODO triage, proposal QA | Minimum viable spec |
| R2 artifact changes | Draft edits, repo patch suggestions, template updates | Minimum spec plus state/artifacts |
| R3 production/client ops | customer workflow, publish prep, deploy prep | Expanded spec, approval gate, rollback/no-op |
| R4 autonomous external action | send, publish, deploy, merge, delete, spend | Do not automate until manual dry runs and reviewer gates pass |

## Maturity Ladder

- **L0**: prompt only. Use when recurrence or verification is weak.
- **L1**: manual loop. Human kicks off; agent returns packet.
- **L2**: stateful manual loop. Reads/writes state and compares to prior runs.
- **L3**: scheduled or event-triggered loop. Still approval-gated.
- **L4**: multi-agent or self-improving loop. Only after stable L2/L3 evidence.

## First Draft Pattern

When details are missing, infer and label assumptions:

```markdown
## Loop Map
- Working name:
- User goal:
- Recurring job:
- Current manual workflow:
- Trigger:
- Source of truth:
- Output packet:
- Done means:
- How it checks:
- Human decision:
- Risk level:
- Recommended archetype:
- Maturity target:
- Best first version:

## Assumptions
- I am assuming...

## Missing Answers
1.
2.
3.

## Recommendation
Prompt first / manual loop / scheduled loop / do not build yet:
```

## Good Onboarding Behavior

- Prefer "Here is the first map; correct the wrong parts" over "please fill out this form."
- If the user is impatient, produce a best-effort map and call out only the blockers.
- If done/check is weak, keep it as a prompt or review checklist.
- If external action is involved, make the first version read-only.
- If state is not useful, do not invent state.
- If the output would create review debt, shrink the scope.
