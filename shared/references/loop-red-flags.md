# Loop Red Flags

Downgrade to a prompt, checklist, or manual dry run when any of these are true:

- The source of truth is not inspectable.
- The agent cannot explain what done means.
- Verification is just "the agent feels satisfied."
- There is no hard stop for time, items, attempts, spend, or subagents.
- The loop can create more review packets than the user can use.
- The task is one-off, exploratory, or mostly taste.
- It can send, publish, deploy, merge, delete, bill, or change customer-facing state without approval.
- It touches production/customer/sensitive data without privacy and logging rules.
- The metric invites Goodharting, such as coverage without assertion quality or SEO samples treated as guaranteed rankings.
- The loop would run on a cadence even when there is no new signal.
- The same agent makes and approves the work on a consequential task.
- There is no persistent state file, score log, issue inventory, or checkpoint.

Safe downgrade options:

- **Prompt first**: use for one-off strategy or ambiguous judgment.
- **Manual dry run**: use once before scheduling.
- **Review queue only**: produce evidence and decision options, no external action.
- **Verifier only**: check work already done rather than doing new work.
- **No-op allowed**: explicitly allow "nothing actionable found" as a terminal state.

## Force Less When

Use the minimum viable spec instead of the expanded spec when:

- The loop only reads sources and produces a short decision packet.
- No external action is possible.
- There is no customer, production, financial, privacy, or destructive surface.
- One manual dry run will prove whether it is useful.
- A one-line answer is enough for a forced field.

Example: a daily decision queue does not need a rollback plan beyond "no state changed." It still needs done criteria, source of truth, hard stop, output packet, approval boundary, no-op condition, and first dry run.
