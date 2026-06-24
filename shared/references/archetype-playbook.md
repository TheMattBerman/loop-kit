# Loop Archetype Playbook

Use this to choose the loop shape and first version.

## Decision Queue Loop

Use when messy inputs need ranked decisions.

- Inputs: TODOs, inbox, worker responses, meeting notes, issue lists.
- Output: ranked queue with decision options and recommended next action.
- Done/check: every item is classified, ranked, and tied to source evidence.
- First version: read-only packet.
- Common mechanics: source freeze, no-op terminal, bounded pass.
- Avoid if: the user expects the loop to execute the decisions autonomously.

## Review Queue Loop

Use when artifacts need approve/fix/reject decisions.

- Inputs: drafts, ads, PRs, proposals, SEO pages, client deliverables.
- Output: decision packet per item.
- Done/check: each item has verdict, reasons, evidence, and next action.
- First version: review 3-10 items manually.
- Common mechanics: evidence packet, maker/checker split, approval gate.
- Avoid if: no rubric exists and taste is fully subjective.

## Verification Loop

Use when the agent can iterate toward a measurable bar.

- Inputs: tests, screenshots, eval scenarios, benchmark data, QA checklist.
- Output: pass/fail result and fixed artifact or issue list.
- Done/check: objective check passes under locked conditions.
- First version: one bounded run with max attempts.
- Common mechanics: benchmark lock, regression capture, bounded pass.
- Avoid if: "good enough" cannot be checked.

## Operating Loop

Use for recurring project, repo, product, or client operations.

- Inputs: state file, logs, tickets, dashboards, calendars, repo status.
- Output: status, exceptions, required decisions, and completed safe actions.
- Done/check: operating surface is reconciled and exceptions are explicit.
- First version: manual weekly/on-demand packet.
- Common mechanics: state ledger, no-op terminal, approval gate.
- Avoid if: it adds operational noise without decision leverage.

## Customer Deployment Loop

Use for getting one client AI workflow from idea to staged rollout.

- Inputs: client context, workflow brief, user roles, constraints, evidence, rollout notes.
- Output: prioritized workflow, dry-run proof, risks, rollout decision.
- Done/check: workflow is tested against real sample inputs and owner approves next stage.
- First version: one workflow, one dry run, one approval packet.
- Common mechanics: dry-run first, approval gate, rollback/reversal, evidence packet.
- Avoid if: there is no owner or no real workflow input.

## Build-Promotion Loop

Use when shipped work needs proof, caveats, screenshots, and promo options.

- Inputs: commits, changelog, demo, screenshots, QA notes, deploy status.
- Output: proof packet plus possible promo angles.
- Done/check: every claim has source proof and caveats are visible.
- First version: on-demand after a build/demo.
- Common mechanics: source freeze, evidence packet, approval gate.
- Avoid if: work is not actually shipped or cannot be shown.

## Compound Learning Loop

Use when repeated corrections should become better skills/templates/gates.

- Inputs: user corrections, rejected outputs, final approved artifacts, failed runs.
- Output: pattern change proposal and patched instruction/template/checker.
- Done/check: correction is turned into a durable change and validated.
- First version: monthly or after 5 corrections.
- Common mechanics: regression capture, state ledger, maker/checker split.
- Avoid if: there are too few examples to distinguish preference from noise.

## Adversarial Review Loop

Use when a plan/proposal/build deserves a skeptic before action.

- Inputs: plan, assumptions, evidence, constraints, target outcome.
- Output: ranked risks, breakpoints, missing proof, revised go/no-go.
- Done/check: key assumptions are tested or clearly marked unresolved.
- First version: one critic pass before approval.
- Common mechanics: maker/checker split, evidence packet, bounded pass.
- Avoid if: the critic has no source material and can only speculate.
