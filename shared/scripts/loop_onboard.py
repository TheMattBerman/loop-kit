#!/usr/bin/env python3
"""Generate a first-pass loop onboarding map from a rough workflow description."""

import re
import sys

GENERIC_TOKENS = {"a", "an", "and", "for", "the", "to", "with", "loop", "agent", "agents", "build"}

ALIASES = {
    "approvals": "approval",
    "clients": "client",
    "corrections": "correction",
    "customers": "customer",
    "drafts": "draft",
    "files": "file",
    "mistakes": "mistake",
    "pages": "page",
    "projects": "project",
    "rollouts": "rollout",
    "skills": "skill",
    "sources": "source",
    "templates": "template",
    "todos": "todo",
    "workflows": "workflow",
}

PHRASE_ALIASES = [
    (re.compile(r"\brolling\s+out\b"), {"rollout", "deployment"}),
    (re.compile(r"\brolled\s+out\b"), {"rollout", "deployment"}),
    (re.compile(r"\bai\s+workflow"), {"workflow", "implementation", "deployment"}),
    (re.compile(r"\bclient[s]?\s+ai\b"), {"client", "customer", "workflow", "deployment"}),
    (re.compile(r"\bsource\s+proof\b"), {"source", "proof", "review"}),
    (re.compile(r"\bpublish\s+readiness\b"), {"publish", "review", "approval"}),
    (re.compile(r"\brecent\s+feedback\b"), {"feedback", "correction", "learning"}),
]

DANGER_PATTERNS = [
    ("vague_done", re.compile(r"\b(until|till|when)\s+(it\s+is\s+|they\s+are\s+|it\s+looks\s+)?(good|better|satisfied|done)\b")),
    ("unsafe_external_action", re.compile(r"\b(send|publish|deploy|merge|delete|spend|post|bill)(?:ing|ed|es|s)?\b|customer-facing update")),
    ("review_debt_machine", re.compile(r"\b(all|every)\s+(active\s+)?(project|projects|todo|todos|draft|drafts)\b")),
    ("unbounded_cadence", re.compile(r"\b(every\s+night|nightly|24/7|always|continuously)\b")),
]

ARCHETYPES = [
    {
        "name": "Decision Queue Loop",
        "keywords": {"decide", "decision", "prioritize", "queue", "todo", "blocked", "inbox", "triage", "rank"},
        "output": "ranked decision queue",
        "risk": "R1 read-only review",
        "maturity": "L1 manual loop",
    },
    {
        "name": "Review Queue Loop",
        "keywords": {"review", "approve", "reject", "draft", "proposal", "asset", "qa", "content", "seo", "client"},
        "output": "approve / fix / reject review packet",
        "risk": "R1 read-only review",
        "maturity": "L1 manual loop",
    },
    {
        "name": "Verification Loop",
        "keywords": {"test", "verify", "check", "benchmark", "screenshot", "regression", "eval", "pass", "fail"},
        "output": "pass/fail packet with evidence and fixes",
        "risk": "R2 artifact changes",
        "maturity": "L2 stateful manual loop",
    },
    {
        "name": "Operating Loop",
        "keywords": {"weekly", "daily", "ops", "operations", "status", "dashboard", "monitor", "cron", "schedule"},
        "output": "operating status and exception packet",
        "risk": "R2 artifact changes",
        "maturity": "L2 stateful manual loop",
    },
    {
        "name": "Customer Deployment Loop",
        "keywords": {"customer", "client", "deployment", "workflow", "rollout", "implementation", "owner", "crm", "approval", "monitoring", "monitor"},
        "output": "workflow rollout decision packet",
        "risk": "R3 production/client ops",
        "maturity": "L2 before scheduling",
    },
    {
        "name": "Build-Promotion Loop",
        "keywords": {"ship", "shipped", "demo", "promo", "promotion", "changelog", "release", "screenshot"},
        "output": "proof, caveats, screenshots, and promo options",
        "risk": "R1 read-only review",
        "maturity": "L1 manual loop",
    },
    {
        "name": "Compound Learning Loop",
        "keywords": {"feedback", "correction", "learning", "skill", "template", "mistake", "pattern", "improve"},
        "output": "durable skill/template/checker change proposal",
        "risk": "R2 artifact changes",
        "maturity": "L2 stateful manual loop",
    },
    {
        "name": "Adversarial Review Loop",
        "keywords": {"critic", "adversarial", "risk", "break", "falsify", "objection", "devil", "review"},
        "output": "risk, breakpoint, and go/no-go packet",
        "risk": "R1 read-only review",
        "maturity": "L1 manual loop",
    },
]

SOURCE_HINTS = [
    ("repo/files", {"repo", "code", "pr", "branch", "commit", "file", "files"}),
    ("TODOs / active work", {"todo", "todos", "task", "blocked", "active"}),
    ("drafts / source docs", {"draft", "drafts", "source", "sources", "doc", "docs", "page", "pages"}),
    ("client/project docs", {"client", "customer", "proposal", "deliverable", "meeting", "call", "workflow"}),
    ("live product/site", {"site", "browser", "prod", "production", "deploy", "payload", "webflow", "publish"}),
    ("analytics/search data", {"seo", "geo", "analytics", "search", "keyword", "traffic"}),
    ("conversation feedback", {"feedback", "correction", "chat", "thread", "skill"}),
]


def normalize_token(token):
    token = ALIASES.get(token, token)
    if token.endswith("ies") and len(token) > 4:
        token = token[:-3] + "y"
    elif token.endswith("ing") and len(token) > 5:
        token = token[:-3]
    elif token.endswith("es") and len(token) > 4:
        token = token[:-2]
    elif token.endswith("s") and len(token) > 3:
        token = token[:-1]
    return ALIASES.get(token, token)


def tokens(text):
    lowered = text.lower()
    found = {normalize_token(token) for token in re.findall(r"[a-z0-9]+", lowered)}
    for pattern, additions in PHRASE_ALIASES:
        if pattern.search(lowered):
            found.update(additions)
    return found - GENERIC_TOKENS


def score_archetypes(query_tokens, raw_text):
    scored = []
    for archetype in ARCHETYPES:
        score = len(query_tokens & archetype["keywords"])
        score += phrase_boost(archetype["name"], raw_text, query_tokens)
        scored.append((score, archetype))
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored


def phrase_boost(archetype_name, raw_text, query_tokens):
    lowered = raw_text.lower()
    score = 0
    if archetype_name == "Customer Deployment Loop":
        if {"client", "customer"} & query_tokens and {"workflow", "deployment", "rollout"} & query_tokens:
            score += 5
        if re.search(r"\brolling\s+out\b", lowered):
            score += 3
        if {"client", "customer", "workflow", "deployment", "rollout"} & query_tokens and {"approval", "monitoring", "monitor"} & query_tokens:
            score += 2
    if archetype_name == "Review Queue Loop":
        if {"draft", "review", "source", "publish"} <= query_tokens:
            score += 4
    if archetype_name == "Compound Learning Loop":
        if {"feedback", "correction"} & query_tokens and {"skill", "template", "learning"} & query_tokens:
            score += 4
    if archetype_name == "Build-Promotion Loop":
        if {"shipped", "demo", "promo", "promotion", "changelog", "release"} & query_tokens:
            score += 3
    if archetype_name == "Operating Loop":
        if {"ops", "operations", "status", "dashboard", "exception"} & query_tokens:
            score += 3
    if archetype_name == "Adversarial Review Loop":
        if {"falsify", "break", "risk", "objection"} & query_tokens:
            score += 4
    return score


def detect_danger_flags(raw_text):
    flags = []
    for label, pattern in DANGER_PATTERNS:
        if pattern.search(raw_text.lower()):
            flags.append(label)
    return flags


def source_guess(query_tokens):
    matches = []
    for label, words in SOURCE_HINTS:
        if query_tokens & words:
            matches.append(label)
    return ", ".join(matches) if matches else "unknown source of truth"


def infer_trigger(query_tokens):
    if {"daily", "weekly", "monthly", "nightly"} & query_tokens:
        return "scheduled cadence mentioned by operator"
    if {"when", "after", "new", "trigger"} & query_tokens:
        return "event-triggered or on-demand after new input"
    return "manual kickoff first; schedule only after a dry run passes"


def recommendation_for(top_score, danger_flags):
    if {"vague_done", "unsafe_external_action"} <= set(danger_flags):
        return "Do not build as written. Convert this to a bounded read-only review or decision queue before any external action."
    if danger_flags:
        return "manual loop first with danger flags resolved before scheduling"
    if top_score > 0:
        return "manual loop first"
    return "prompt/checklist first until the job is clearer"


def missing_questions(source, archetype, query_tokens):
    questions = []
    if source == "unknown source of truth":
        questions.append("What should the loop inspect as the source of truth?")
    if not ({"done", "check", "verify", "test", "score", "approve", "reject"} & query_tokens):
        questions.append("What would make one run count as done, and how should the agent check it?")
    if {"send", "publish", "deploy", "merge", "delete", "spend", "bill", "customer", "client", "rollout"} & query_tokens:
        questions.append("What actions require explicit human approval before the loop can take them?")
    else:
        questions.append("What should the loop hand back to the human for a decision?")
    return questions[:3]


def map_loop(text):
    """Analyze a rough workflow description and return a loop onboarding map.

    Returns a dict with keys:
        archetype (str): best-fit archetype name or 'Unclear'
        recommendation (str): guidance string; contains 'Do not build as written'
                              when vague_done and unsafe_external_action co-occur
        flags (list[str]): danger flags detected (e.g. 'vague_done',
                           'unsafe_external_action', 'review_debt_machine')
        done (str): how done/check is inferred for this loop
        source (str): likely source of truth
        trigger (str): inferred trigger type
        output (str): likely output packet for the top archetype
        risk (str): risk level for the top archetype
        maturity (str): maturity starting point for the top archetype
        secondaries (list[str]): names of runner-up archetypes with score > 0
        _top_archetype (dict): raw archetype dict for the top match (for internal use)
        _query_tokens (set): tokenized query (for internal use)
    """
    raw = text.strip()
    q = tokens(raw)
    danger_flags = detect_danger_flags(raw)
    scored = score_archetypes(q, raw)
    top_score, top = scored[0]
    source = source_guess(q)
    recommendation = recommendation_for(top_score, danger_flags)
    trigger = infer_trigger(q)
    secondaries = [a["name"] for score, a in scored[1:4] if score > 0]

    done_tokens = {"done", "check", "verify", "test", "score", "approve", "reject"}
    if done_tokens & q:
        done = "explicit done/check signal present in description"
    else:
        done = "not specified; operator must define the done/check pair before scheduling"

    return {
        "archetype": top["name"] if top_score > 0 else "Unclear",
        "recommendation": recommendation,
        "flags": danger_flags,
        "done": done,
        "source": source,
        "trigger": trigger,
        "output": top["output"] if top_score > 0 else "decision/review packet",
        "risk": top["risk"] if top_score > 0 else "R0/R1",
        "maturity": top["maturity"] if top_score > 0 else "L0 prompt or L1 manual loop",
        "secondaries": secondaries,
        "_top_archetype": top,
        "_query_tokens": q,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: loop_onboard.py <rough workflow description>", file=sys.stderr)
        return 2

    raw = " ".join(sys.argv[1:]).strip()
    result = map_loop(raw)

    print("## Loop Onboarding Map")
    print(f"- Rough input: {raw}")
    print(f"- Recommended archetype: {result['archetype']}")
    if result["secondaries"]:
        print(f"- Secondary mechanics/archetypes to consider: {', '.join(result['secondaries'])}")
    print(f"- Likely source of truth: {result['source']}")
    print(f"- Likely trigger: {result['trigger']}")
    print(f"- Likely output packet: {result['output']}")
    print(f"- Risk starting point: {result['risk']}")
    print(f"- Maturity starting point: {result['maturity']}")
    print(f"- Best first version: {result['recommendation']}")
    if result["flags"]:
        print(f"- Danger flags: {', '.join(result['flags'])}")
    print()
    print("## Missing Answers")
    for i, question in enumerate(
        missing_questions(result["source"], result["_top_archetype"], result["_query_tokens"]),
        start=1,
    ):
        print(f"{i}. {question}")
    print()
    if result["flags"]:
        print("## Recommendation")
        print(result["recommendation"])
        print()
    print("## Design Warning")
    print("Do not schedule or externalize this loop until a manual dry run proves the done/check pair works.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
