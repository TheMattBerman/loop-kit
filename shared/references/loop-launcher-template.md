# Loop Launcher Template

Use this when the operator wants a copy-paste prompt to start a manual dry run or create a scheduled automation later.

Use the first version as a read-only or approval-gated dry run unless the operator explicitly approved execution.

```markdown
Use the loop spec below. Run only the first manual dry run. Do not schedule, send, publish, merge, deploy, delete, or change production/customer-facing state.

Your job:
<job>

Source of truth:
<files/repos/tools/live systems>

Done means:
<checkable done criteria>

How to check:
<tests, scorecard, source proof, screenshot, benchmark, review packet>

Hard stops:
- Max time:
- Max items:
- Max attempts:
- Stop if blocked by:

Allowed actions:
<allowed>

Approval required before:
<approval boundary>

Output packet:
Return:
1. What you inspected
2. What changed, if anything
3. Evidence
4. Blockers
5. Recommended next decision
6. Whether this should become a scheduled loop
```

## Handoff Version

Use this when launching the loop in a fresh agent thread:

```markdown
Before acting, read the relevant route cards and output the applicable packet.

You are running a manual dry run of this loop, not scheduling it.

Loop name:
<name>

Loop map:
<job, trigger, source, output, done/check, approval boundary>

Allowed:
<read/write actions allowed>

Forbidden without approval:
send, publish, deploy, merge, delete, spend, customer-facing changes, or any action listed here: <specific forbidden actions>

Hard stops:
<caps and blocked conditions>

Return the output packet exactly as specified:
<packet format>
```
