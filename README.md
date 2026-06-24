# loop-kit

<p>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License" />
  <img src="https://img.shields.io/badge/Claude%20Code-plugin-6D28D9?style=for-the-badge" alt="Claude Code Plugin" />
  <img src="https://img.shields.io/badge/Codex-plugin-0F766E?style=for-the-badge" alt="Codex Plugin" />
  <img src="https://img.shields.io/badge/Beginner-friendly-F43F5E?style=for-the-badge" alt="Beginner Friendly" />
</p>

**Make killer loops.**

You should not have to prompt your AI all day. loop-kit turns a rough recurring job into a safe supervised first run, even if you have never heard the word "loop." It talks in plain English, designs the loop, creates the checkpoint packet, captures evidence, asks only for missing judgment or approval, and tells you whether the loop is ready to graduate.

Built for Claude Code, Codex, and any agent that reads skills. Three skills, one install.

**Built by Matthew Berman.**

> **See it work first:** you talk to it in plain English. It answers in plain English. The codes stay hidden.

<p align="center">
  <img src="assets/loop-start-demo.gif" alt="loop-start turns a plain-English request into a jargon-free plan" width="900" />
</p>

---

## prompt-jail is the slow way to use AI

You open your laptop and start typing to your AI. Again. Paste the context, ask the question, copy the answer, repeat. Same thing tomorrow. That is prompt-jail, and it is the slow way to use AI.

A loop is just AI doing a job for you on repeat, with a clear source, a clear definition of done, and a way to check its work:

- check competitor prices every morning and tell you what changed
- review your drafts before they publish
- sort your inbox and surface what actually matters
- turn this week's wins into a promo draft

You describe the job once. loop-kit turns it into a first-run system you can supervise. The catch most "automate everything" advice skips: handing AI the keys is a little scary. loop-kit keeps send, post, publish, deploy, merge, delete, spend, billing, and customer-facing actions behind approval.

---

## start here: tell it what you want

```
/loop-start
> I want AI to check my competitors' prices every morning and tell me what changed.
```

loop-start asks if you want the quick version or the full walk-through, then a plain question or two, and hands you something you can run:

```text
Here is what your loop will do:
  A job that checks your competitors' prices each morning and flags what moved.

What it does on its own / what it checks with you first:
  On its own: reads the prices, compares to yesterday, writes you a short summary.
  Checks with you first: nothing gets sent or posted anywhere without your OK.

Your runnable system (paste this into your agent):
  Each morning, open the competitor list. For each one, read today's price and
  compare it to the saved price from yesterday. Write a short summary of what
  changed. Save the new prices. Do not email or post anything; leave the summary
  for me to read.

Try it once like this:
  I will run the first version safely, with checkpoints. Run it by hand tomorrow on
  2 or 3 competitors. Check the summary before you consider any repeat schedule.
```

You never see a risk code or an architecture term. You describe the job, you get a first-run system, and the kit tells you what evidence is missing before anything graduates.

---

## the three skills

```text
            you describe the job, in plain english
                          |
                     /loop-start          <- start here
                    /          \
          /loop-builder       guarded by /loop-doctor
       the full design          the safety check that
     (map, spec, dry run)       runs underneath them all
```

| Skill | What it does | For |
|---|---|---|
| `loop-start` | Plain language. Asks what you want, builds it, walks you through it. | Anyone. Start here. |
| `loop-builder` | The full design: map, spec, callable prompt, dry run. | When you know what you want. |
| `loop-doctor` | Audits a loop before you run it and says where it will hurt you. | The safety check, always on underneath. |

loop-doctor is the reason you can trust the rest. It is what stops the system from quietly automating something it shouldn't.

---

## under the hood (for the technical crowd)

The safety is not vibes, it is code. `validate_spec.py` structurally enforces the fields a real first run needs: source of truth, done criteria, verification method, approval boundary, hard stops, no-op condition, output packet, and first manual dry run. Higher-risk or external-action loops also require tools/permissions, state, artifacts, maker/checker split, schedule decision, and approval artifact.

```bash
$ python3 shared/scripts/validate_spec.py spec.md
{ "verdict": "FAIL", "missing": ["verification_method", "approval_boundary"], "vague": [] }
```

loop-start runs this for you and translates the result into plain English. The engine can return `go`, `fix-then-go`, `downgrade-to-prompt`, or `not-a-loop`. A non-technical user never sees those words; loop-start says things like "this one is better with you in the driver's seat, here is a safer version."

The checkpoint layer creates local run packets:

```text
.loop-kit/<loop-slug>/
  spec.md
  runs/<run-id>/
    checkpoint.json
    source-freeze.md
    output-packet.md
    blockers.md
    approval-request.yaml
```

It can close a first run as `manual_pass`, `fix_then_rerun`, `no_op`, `blocked`, `do_not_schedule`, `failed_verification`, `approval_required`, or `exhausted`. It never emits `scheduled`; a clean first run can only return `safe_to_consider_scheduling`.

The graduation layer can create schedule-readiness proposals and run local/sandbox recurrence checks with ledgers and pause reasons. It helps you prove a loop is ready for a real scheduler, but you still own the actual scheduler wiring.

The Goal Orchestrator layer is for iterative agent work. It turns a high-level objective into measurable criteria, writes worker and reviewer packets, parses result reports, decides pass/fail/needs-fix/blocked, and writes the next goal prompt. If real connector authorization or production scheduling is needed, it gives user-owned setup instructions instead of secretly connecting tools or installing background jobs.

It also names the failure modes the hype skips, and tracks one number most people miss:

| What it catches | Why it matters |
|---|---|
| **Ralph Wiggum loop** | A soft "done" that hides a half-finished job |
| **Comprehension debt** | A system that works until nobody understands it |
| **Cognitive surrender** | Trusting output you stopped checking |
| **The security tax** | Unattended agents are an attack surface |
| **Cost per accepted change** | Under 50% accepted means the loop is making noise, not value |

---

## quickstart

```bash
# 1. clone
git clone https://github.com/TheMattBerman/loop-kit.git
cd loop-kit

# 2. inspect the install target without writing files
bash install.sh --runtime both --dry-run

# 3. install (claude, codex, or both)
bash install.sh --runtime claude

# 4. verify
bash doctor.sh
```

Installed to `~/.claude/skills/loop-kit/` and/or `~/.codex/skills/loop-kit/`. The skills and their shared scripts travel together, so everything resolves from the kit root.

Then, in Claude Code or Codex, say `/loop-start` (or `@loop-start` in Codex) and tell it what you want. Technical and want the full design or a safety audit? Call `/loop-builder` or `/loop-doctor` directly.

---

## the pattern library

loop-kit ships an index of proven loop shapes from three public sources, so it can point you at one that already works instead of inventing one. The index carries titles, slugs, URLs, and original commentary only. No prompt bodies or proprietary content from any source are reproduced here.

| Source | Where |
|---|---|
| Forward Future Loop Library (Matthew Berman, no affiliation with this project) | <https://signals.forwardfuture.ai/loop-library/> |
| Anthropic, Building effective agents | <https://www.anthropic.com/research/building-effective-agents> |
| LangGraph / LangChain AI | <https://langchain-ai.github.io/langgraph/> |

See [SOURCES.md](SOURCES.md) for the full index and [NOTICE](NOTICE) for attribution details.

---

## honest limits

This gets AI working for you. It is not magic.

- It does not guarantee the loop is perfect. The safety check makes sure the loop is built right, not that the job you described was the right job.
- It does not replace your judgment. The first manual run and the occasional spot-check are on you. Skipping that first by-hand run is the most common way a good loop goes wrong.
- It does not catch every risk. It covers the common failure modes. Never treat a green light as a blank check.
- It does not create production recurring schedules. Graduation is approval-gated and evidence-gated; local/sandbox recurrence checks are proof artifacts, not installed jobs.
- It does not secretly authorize connectors. You own real connector setup and paste evidence back for review.

---

## more operator kits

loop-kit sits in the same family as the rest of the agent kit stack:

- [Frontrun](https://github.com/TheMattBerman/frontrun) - paste a URL, get to the angle before your competitors do
- [Short-Form Idea Engine](https://github.com/TheMattBerman/shortform-idea-engine) - competitor videos to ranked, brand-fit scripts

loop-kit owns the on-ramp: the layer that gets AI working for you on repeat, safely, even if you are not technical.

---

## license

MIT. See [LICENSE](LICENSE). Fork it. No upsell, no catch.

---

Built by [Matt Berman](https://twitter.com/themattberman).

- Twitter/X: [@themattberman](https://twitter.com/themattberman)
- Newsletter: [Big Players](https://bigplayers.co)
---

Stop prompting your AI all day. Start building loops that can prove their work.
