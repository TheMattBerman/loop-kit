# Loop Spec Template

Use this template when designing a real loop.

Start with the loop map. Do not skip it unless the user already provided the equivalent details.

```markdown
# Loop: <name>

## Recommendation
Build / do not build / prompt first:
Reason:

## Loop Map
Working name:
User goal:
Recurring job:
Current manual workflow:
Trigger:
Source of truth:
Output packet:
Done means:
How it checks:
Human decision:
Risk level:
Recommended archetype:
Maturity target:
Best first version:

## Archetype
Primary archetype:
Secondary reusable mechanics:

## Job
Recurring pain:
Agent role:
Human owner:
User-visible outcome:

## Use When
Prerequisites:
Trigger conditions:
Good fit because:

## Do Not Use When
Bad-fit conditions:
Missing source/gate/tooling:
Use a prompt instead if:

## Maturity
Level:
Catalog class, if adapted from Forward Future:
Why:

## Catalog Pattern
Forward Future pattern:
Adapted from:
What changes for your context:

## Trigger
Type: message / cron / heartbeat / hook / goal / nested goal
Exact trigger:
No-new-signal behavior:

## Source Of Truth
Files:
Repos:
Tools/APIs:
Live systems:
Required credentials/connectors:

## Inputs
Data window:
Examples/scenarios:
Benchmark conditions:
Current-state capture:

## Tools
Commands:
MCP/connectors:
Browser/live proof:
Scripts/checkers:
Subagents:

## Permissions
Read allowed:
Write allowed:
External actions allowed:
Approval required before:
Forbidden:

## State
State file:
Run artifacts:
What to read at start:
What to update at end:

## Run Steps
1.
2.
3.
4.

## Done Criteria
Done means:
Not done if:

## Verification
Objective checks:
Subjective rubric, if unavoidable:
Evidence required:
Who/what checks:

## Maker / Checker Split
Maker:
Checker:
Independence rule:

## Hard Stops
Max time:
Max items:
Max iterations:
Max subagents:
Max spend:
Escalate when:

## Stop Conditions
Pass:
No-op:
Blocked:
Retry cap:
Budget cap:
Stalemate:

## Human Approval Boundary
Allowed without approval:
Requires approval:
Forbidden:

## Output Packet
Format:
Required fields:
Decision options:
No-op output:

## Risks And Rollback
Risks:
Goodhart/overfit risk:
Privacy/security risk:
Rollback or reversal:

## First Manual Dry Run
Command/prompt:
Expected artifact:
Pass/fail bar:
Next scheduling decision:
```

## Minimum Viable Spec

For low-risk L1-L2 loops, use this shorter version:

```markdown
# Loop: <name>

## Recommendation

## Archetype

## Use When

## Do Not Use When

## Trigger

## Source Of Truth

## Done Criteria

## Verification

## Hard Stops

## Output Packet

## Approval Boundary

## No-op Condition

## First Manual Dry Run
```

## Minimal STATE.md

```markdown
# Loop State: <loop name>

## Purpose

## Current Status
- status:
- last_run:
- next_run:
- owner:

## Inputs
- source files:
- repos:
- APIs/tools:
- TODOs:

## Last Run
- date:
- commands/actions:
- artifacts:
- result:

## Queue
| Item | Status | Evidence | Next action |
|---|---|---|---|

## Gates
- required checks:
- hard stops:
- human approval needed before:

## Blockers
- blocker:
- owner:
- needed decision:

## Lessons
- YYYY-MM-DD:
```
