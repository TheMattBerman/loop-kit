# Loop Composition

This reference covers three patterns that appear once a team is running more than one loop. Each section has a worked generic example.

---

## 1. Loop-Stack / Packet-Handoff Model

### The problem with one mega-loop

When a single loop owns too many stages -- discovery, production, QA, release, promotion -- the approval boundary becomes impossible to draw. Everything depends on everything else. A failure in one stage poisons the others. Rollback is unclear. Auditability is low.

The better shape is a stack of bounded loops. Each loop owns one stage. Each loop hands a typed packet to the next.

### What "bounded" means

A loop is bounded when:

- It has one job.
- It has a single output packet type.
- Done is checkable without running the next stage.
- It can terminate cleanly with a no-op if there is nothing to act on.

### The packet-handoff contract

The packet handed from one loop to the next should be:

- **Typed**: the receiving loop knows exactly what fields to expect.
- **Source-attributed**: every item in the packet carries its origin (file, URL, timestamp).
- **Decision-complete**: each item has a verdict and a recommended next action.
- **Bounded**: the packet caps the number of items so the next loop is not overwhelmed.

### Worked example: a SaaS content team

A SaaS content team runs the following stack:

| Loop | Job | Input | Output packet | Handoff trigger |
|---|---|---|---|---|
| Opportunity loop | Find useful search opportunities | Keyword data, competitor gap analysis | Brief queue (max 10 items, ranked) | New brief queue file written |
| Draft loop | Turn brief into draft | Brief queue | Draft file per slug | Draft file committed |
| Editorial QA loop | Approve, fix, or reject each draft | Draft files | Decision packet per slug | Decision packet written |
| Image loop | Generate and review assets | Approved slugs from decision packet | Image manifest per slug | Manifest committed |
| CMS release loop | Attach assets and metadata, dry-run | Image manifest, approved decision packet | Release manifest (dry-run output) | Release manifest approved by operator |
| Publish loop | Execute schedule or publish | Approved release manifest | State update, commit, push | Run complete |
| Post-release loop | Monitor and learn | Published URLs, analytics signal | State update with lessons | Run after 7-day signal window |

Each loop reads the previous loop's output packet. It does not reach back into earlier stages. If the editorial QA loop rejects a slug, that slug does not enter the image loop. The handoff is clean.

### What to avoid

- Loops that read state from two stages back (hidden coupling).
- Packets with unbounded item counts (the next loop cannot cap its work).
- Loops that modify items already owned by the next stage (write conflicts).
- Skipping the packet and passing a live system reference instead of a frozen artifact.

---

## 2. Claim-Ledger Gate

### The problem with link count as a proxy for proof

A common hygiene gate counts external links. Two links per page sounds like proof discipline. It is not. Two links do not support twenty claims. A link count is a density proxy, not a source-to-claim binding.

The real gate is per-claim source binding: for each strong claim in an artifact, record exactly which source supports it, whether that source permits public use, and whether the exact wording is allowed.

### When to require a claim ledger

Require a claim ledger before any artifact is released when:

- The artifact makes numerical claims (metrics, costs, conversion rates, rankings).
- The artifact makes client or case-study claims.
- The artifact is in a high-risk vertical (legal, healthcare, financial, paid media).
- The artifact will be public and attributable to the organization.

For low-risk internal artifacts, a simpler source-freeze is enough.

### Ledger structure

```yaml
claims:
  - claim: "Teams using this workflow ship 30% faster."
    claim_type: metric
    source_url_or_internal_proof: "https://example.com/study"
    approved_public_use: true
    exact_text_allowed: true
    risk_level: medium

  - claim: "Reduces onboarding time by half."
    claim_type: client_result
    source_url_or_internal_proof: "internal-case-study-acme.md"
    approved_public_use: false
    exact_text_allowed: false
    risk_level: high
```

### Fail-closed on high-risk claims

The gate should be fail-closed: if a high-risk claim has no ledger entry, the artifact does not proceed to the next stage. The agent flags the gap and stops. The operator decides whether to add proof, weaken the claim, or remove it.

### Worked example: a SaaS blog post

An operator is publishing a post about AI-assisted customer support. The draft contains three strong claims:

1. "Our customers see 40% faster ticket resolution."
2. "AI handles 60% of tier-1 tickets automatically."
3. "Most SaaS teams spend $15-25k per year on tier-1 support."

The claim-ledger gate runs before scheduling:

- Claim 1: client result. Source = internal case-study doc. Approved for public use? Not yet -- flagged. Loop stops here.
- Claim 2: metric from a specific customer. No ledger entry. Flagged.
- Claim 3: cost range from a market report. Source URL provided. Approved. Passes.

The operator reviews the two flags, decides to either add proof or soften the language, and reruns the gate. Only then does the artifact advance.

### What to avoid

- Using link count as a claim-proof substitute.
- Running the ledger check after scheduling has already happened.
- Treating "generally accepted" or "we believe" as sufficient for numerical claims.
- Allowing the same agent that wrote the claims to approve them without a checker.

---

## 3. Deterministic-Hygiene vs. Semantic-Editorial Two-Tier Gate

### The problem with trusting automated scans

Deterministic scans are fast and repeatable. They catch link counts, banned phrases, contraction ratios, direct-address signals, and formatting rules. They are useful and should be required.

They cannot catch:

- Whether a source actually supports a claim.
- Whether the opener has a real point of view.
- Whether the page will be readable on mobile.
- Whether a list collapsed during CMS import.
- Whether the CTA moves the reader to the right next step.
- Whether the tone talks to the reader or about the reader.

Treating deterministic checks as full editorial approval is the mistake. A post can pass every automated gate and still be unacceptable for release.

### Two-tier structure

**Tier 1 -- Deterministic hygiene gate (automated, required, fast):**

- Link count check.
- Banned phrase scan.
- Contraction count.
- Direct-address signal count.
- Metadata completeness (title, description, author, reviewer fields).
- Asset existence check (featured image, inline images present).
- Hard-coded internal path scan.
- Public-URL reachability spot check.

**Tier 2 -- Semantic and editorial gate (rendered output, human or LLM reviewer, required before release):**

- Does the rendered page look correct? (H1 visible, reviewer visible, images framed, CTA present.)
- Is the opener reader-facing or about-the-audience?
- Does the article answer the search job or wander?
- Does the CTA point to the right destination?
- Is the article distinct from existing articles on similar topics?
- Is list/table formatting intact after CMS import?
- Is the page digestible on mobile?

Neither tier substitutes for the other. A post that fails Tier 1 should not reach Tier 2 review. A post that passes Tier 1 but has not been reviewed at Tier 2 is not ready to release.

### Rendered/real-output verification

Tier 2 requires inspecting the actual rendered output, not just the source file or CMS record. A database record and a rendered page are different things. The page can import correctly but render incorrectly because of:

- Rich-text import collapsing lists into plain text.
- Image node rendering at the wrong position or size.
- Duplicate FAQ blocks from import artifacts.
- Missing reviewer byline from a metadata field mismatch.
- CTA component pointing to a stale or wrong URL.

The only way to catch these is to inspect the rendered page, either via screenshot, browser automation, or a human review step.

### Worked example: a content team's release gate

A content team publishes blog posts for a B2B SaaS product. Before any post is scheduled, two gates must pass:

**Tier 1 (automated, runs on every draft):**

```bash
node scripts/check-draft-quality.mjs --slug "ai-support-guide"
```

Checks: contraction count >=8, direct-address signals >=3, no banned phrases, external links >=2, metadata fields complete, featured image exists. Fast. Runs in seconds.

**Tier 2 (rendered review, runs only on drafts that pass Tier 1):**

The reviewer opens the staging URL for the post and confirms:

- H1 is correct.
- Reviewer byline is visible.
- Featured image is framed correctly.
- Inline image appears at the right location in the body.
- FAQ section renders once, not twice.
- CTA is present and links to the correct service page.
- No text overlaps images.
- Mobile screenshot is readable.

Only posts that pass both tiers enter the schedule manifest.

### What to avoid

- Declaring a post "gate-passed" after Tier 1 only.
- Running Tier 2 on unrendered source files instead of the actual page.
- Letting the same agent that authored the post approve it at Tier 2 without a separate checker.
- Skipping Tier 2 on time pressure and planning to "check it after it goes live."
