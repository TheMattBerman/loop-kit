# Forward Future Loop Library Analysis

Source: the Forward Future loop library catalog, 31 loops.

## Common Loop Schema

Every useful loop spec should include:

- `useWhen`: when this loop applies and when it does not.
- `prompt`: the callable job prompt.
- `verification`: what done means and how to stop.
- `steps`: the real run behavior.
- `why`: why this loop creates leverage.
- `implementationNote`: the risk, permission, or measurement caveat.
- `related`: adjacent patterns to combine or compare.

For your context, also add:

- source of truth
- state location
- output packet
- hard stops
- maker/checker split
- approval boundary
- first manual dry run

## Maturity Ladder

Use this as the operating ladder:

- **L0**: prompt only. Use when recurrence or verification is weak.
- **L1**: manual loop. Human kicks off; agent returns packet.
- **L2**: stateful manual loop. Reads/writes state and compares to prior runs.
- **L3**: scheduled or event-triggered loop. Still approval-gated.
- **L4**: multi-agent or self-improving loop. Only after stable L2/L3 evidence.

> **Catalog cross-reference note:** The Forward Future catalog also uses M1-M4 maturity classes (M1 bounded audit/fix, M2 measured iteration, M3 operational/production, M4 agentic system). These are catalog labels for organizing example patterns -- they do not replace the L0-L4 operating ladder above. When you see M1-M4 in catalog entries below, treat them as a secondary classification for cross-referencing patterns, not as a separate progression to follow.

## Loop Archetypes

Use these as the main "shape" before selecting a Forward Future pattern:

| Archetype | Primary output | Best for | Common patterns |
|---|---|---|---|
| Decision Queue Loop | Ranked decisions | open TODOs, blockers, calendar-sensitive work | no-op terminal, bounded pass, evidence packet |
| Review Queue Loop | approve/reject/fix packets | drafts, PRs, client deliverables, creative assets | source freeze, approval gate, maker/checker |
| Verification Loop | pass/fail proof | product QA, tests, screenshots, benchmarks | benchmark lock, regression capture, hard stops |
| Operating Loop | terminal state or handoff | repo maintenance, releases, production, data cleanup | state ledger, approval gate, rollback |
| Customer Deployment Loop | rollout evidence | client AI workflows and customer processes | dry-run first, monitoring, staged approvals |
| Build-Promotion Loop | proof/caveat/promo packet | shipped features, demos, free tools | source freeze, evidence packet, approval gate |
| Compound Learning Loop | skill/template/checker updates | repeated corrections and quality misses | recent-feedback, docs sweep, completion contract |
| Adversarial Review Loop | objection log and resolution | proposals, architecture, launches, strategy | independent critic, stalemate state, acceptance bar |

## Reusable Mechanics

Reusable mechanics are plug-ins, not mandatory decorations:

- **Source freeze**: capture the current repo state, page, thread, data window, release identity, transcript, screenshot, or benchmark conditions before acting.
- **State ledger**: update `STATE.md`, issue inventory, score log, checkpoint, baseline, or baton.
- **Maker/checker split**: separate the producing agent from the evaluating agent.
- **No-op terminal**: allow clean stop when nothing actionable exists.
- **Bounded pass**: cap items, minutes, attempts, spend, or subagents.
- **Evidence packet**: require proof for every recommendation.
- **Approval gate**: hold send/publish/deploy/merge/delete/customer-facing actions.
- **Regression capture**: preserve failed examples as future checks.
- **Benchmark lock**: use the same test conditions for every rerun.
- **Dry-run first**: prove the loop manually before scheduling.
- **Downgrade rule**: use a prompt/checklist when source, done criteria, or verification is weak.

## Forced Items By Risk

Use forced fields as a validity gate, not bureaucracy.

### Minimum viable spec

For L1-L2 loops, require:

- archetype
- use_when
- do_not_use_when
- trigger
- source_of_truth
- done_criteria
- verification_method
- hard_stops
- output_packet
- approval_boundary
- no_op_condition
- first_manual_dry_run

### Expanded spec

For L3-L4 loops, customer work, production, external action, or destructive work, also require:

- catalog_pattern
- inputs
- tools_and_permissions
- state_location
- run_artifacts
- steps
- maker_checker_split
- stop_conditions
- risks
- rollback_or_reversal
- schedule_decision

## Catalog Taxonomy

### Engineering

1. **The docs sweep**: M1. Fixes documentation drift after implementation changes. Good L2/L3 if commands/examples can be verified.
2. **The architecture satisfaction loop**: M2. Incremental refactor with live-test, autoreview, and progress file. Dangerous unless "satisfactory" is defined up front.
3. **The sub-50 ms page-load loop**: M2. Performance loop with fixed benchmark. Good L3 when metric/environment are explicit.
4. **The production error sweep**: M3. Production telemetry to root cause to reviewable PR. L4; requires sensitive-log boundaries.
5. **The 100% test coverage loop**: M2. Coverage target with suite proof. L3; needs test-quality review.
7. **The logging coverage loop**: M2. Adds tested observability across important paths. L3; never log secrets.
8. **The nightly changelog loop**: M3. Turns product changes into user-facing release notes. L1/L2; verify against actual behavior, not commit titles.
11. **The test-suite speed loop**: M2. Improves CI/local test speed without coverage/behavior regression. L3.
12. **The repository cleanup loop**: M1. Audits branches, PRs, commits, and worktrees. L2 unless destructive cleanup is approved.
16. **The ticket-to-PR-ready loop**: M1. Reproduces, fixes, verifies, and packets a bug. L3/L4.
19. **The Clodex adversarial-review loop**: M4. Independent reviewer loops over repair rounds. L3.
20. **The Loop Harness verification loop**: M4. One agent cannot approve its own output. L3/L4.
25. **The fresh-clone loop**: M2. Tests onboarding from a clean environment. L3.
27. **The autonomy-loop builder-reviewer loop**: M4. Repeated builder/reviewer handoffs with deterministic gates. L4.
28. **The Codex completion-contract loop**: M4. Audits long-running agent work against explicit completion proof. L2/L3.
30. **The five-minute repository maintainer loop**: M4. Heartbeat repository maintenance across active repos. L4; observation is not authority.
31. **The recent-feedback sweep**: M2. Finds repeated feedback patterns and closes the issue inventory. L2/L3; ideal for compound learning.

### Content

6. **The SEO/GEO visibility loop**: M2. Crawl, indexation, intent, citations, and answer-readiness with repeatable benchmark. L2/L3.
18. **The product update podcast loop**: M3. Release changes to short audio episode. L2; ask before publishing.

### Evaluation

9. **The quality streak loop**: M2. Realistic scenarios must pass N times in a row; failures become regression coverage. L3.
10. **The full product evaluation loop**: M2. Scenario coverage across all major capabilities. L3.
23. **The self-improving champion loop**: M2. Tune prompt/policy/config with holdout evaluation. L3; separate working set and holdout.
24. **The devil's-advocate loop**: M2. Adversarial review before consequential decisions. L2/L3.
29. **The Revolve versioned-experiment loop**: M4. Versioned experiments with comparable checkpoints. L3.

### Operations

13. **The stale-safe batch release loop**: M3. Combines valid changes while excluding stale work. L4.
14. **The production data cleanup loop**: M3. Review records, fix classifier, verify retained data. L4; reversible operations and approval.
15. **The post-release baseline loop**: M3. Records benchmark baseline after release. L2/L3.
17. **The customer AI deployment loop**: M3. Validates one customer workflow through approvals, rollout, monitoring, and outcome evidence. L4; best client-delivery fit.

### Design

21. **The Boeing 747 benchmark**: M2. Three.js capture-and-critic visual benchmark. L3.
22. **War Loops: frontend reconstruction**: M2. Rebuild authorized UI from URL/image and compare appearance/motion/responsiveness. L3; requires authorization.
26. **The Infinite Clickbait thumbnail loop**: M2. Thumbnail ideation and critique rounds. L2/L3; avoid misrepresentation.

## Pattern Selector

Map requests to one of these families before writing a loop:

- **Audit/fix**: docs sweep, repository cleanup, ticket-to-PR, recent-feedback.
- **Benchmark**: sub-50ms, fresh clone, Boeing 747, SEO/GEO.
- **Streak eval**: quality streak, full product evaluation.
- **Release ops**: nightly changelog, stale-safe batch release, post-release baseline.
- **Customer deployment**: customer AI deployment, production data cleanup.
- **Critic-builder**: Clodex, Loop Harness, autonomy-loop, devil's advocate.
- **Self-improvement**: self-improving champion, Revolve.
- **Multi-agent harness**: five-minute maintainer, completion-contract, autonomy-loop.

## High-Value Adaptations By Loop Family

### Daily Decision Queue

Pattern sources: nightly changelog, recent-feedback sweep, repository maintainer.

Use for: active TODOs, blocked work, worker responses, and calendar-sensitive decisions.

Stop: top 5 decisions with file paths and recommended answer.

Boundary: do not close tasks or send messages without approval.

### Content Review Queue

Pattern sources: SEO/GEO visibility loop, quality streak, full product evaluation.

Use for: content drafts, source proof, content gates, internal queue state.

Stop: top 3 drafts have pass/fail, blockers, evidence, and next decision.

Boundary: no publish, index, deploy, or ready-status flip without approval.

### Build-Promotion Packet

Pattern sources: nightly changelog, post-release baseline, full product evaluation.

Use for: shipped builds, demos, merged PRs, free tools, client-facing features.

Stop: packet has what changed, who cares, proof, screenshots, caveats, and promo options.

Boundary: no public post/email/client update without approval.

### Client AI Deployment Review

Pattern sources: customer AI deployment loop, quality streak, production data cleanup.

Use for: one client workflow priority at a time.

Stop: dry-run evidence, owner, inputs, approval state, rollout stage, monitoring, and ROI hypothesis.

Boundary: no rollout expansion or customer-facing change without approval.

### Recent Feedback Sweep

Pattern sources: recent-feedback sweep, completion-contract loop, docs sweep.

Use for: repeated user corrections, skill/template/checker updates, compound learning.

Stop: issue inventory closed and fresh pattern audit clean.

Boundary: no broad skill rewrites without review if multiple workflows are affected.

## Bad-Fit Red Flags

- "Done" is subjective and no rubric/checker exists.
- The loop needs private/customer/production data but has no permission plan.
- It creates more review packets than the operator can use.
- It runs on a cadence with no new signal.
- It can send, publish, deploy, merge, delete, or spend without approval.
- It can spawn subagents without a cap.
- It is compensating for unclear strategy rather than repeated execution.
- The source of truth is not inspectable by the agent.
- The task is one-off, exploratory, or mostly taste.
