# shared/scripts/plain_language.py
"""Map loop-kit engine codes to everyday English for the beginner front door."""

_ARCHETYPE = {
    "decision queue": "a job that sorts your open work into clear next decisions",
    "review queue": "a job that reviews items and returns approve, fix, or reject",
    "verification": "a job that checks something and flags what is wrong",
    "operating": "a job that handles a recurring task and keeps it running",
    "customer deployment": "a job that takes one workflow live for a customer, step by step",
    "build-promotion": "a job that turns finished work into proof and promo options",
    "compound learning": "a job that turns repeated corrections into reusable improvements",
    "adversarial review": "a second opinion that tries to poke holes before you commit",
}
_RISK = {
    "0": "it only reads and suggests",
    "1": "it only reviews and flags, it does not change anything",
    "2": "it changes files, so give it a careful first run",
    "3": "it can take real actions, so keep a close eye on it",
    "4": "it can act on the outside world, so it needs your approval and limits",
}
_MATURITY = {
    "0": "you can do this with a single prompt for now",
    "1": "start by running it yourself a few times before automating",
    "2": "run it yourself and let it keep simple notes between runs",
    "3": "once it is proven, it can run on a schedule with checkpoints",
    "4": "this is a full system, only after many proven runs",
}
_VERDICT = {
    "go": "This is a good fit to set up.",
    "fix-then-go": "Almost there. Fix one or two things first.",
    "downgrade-to-prompt": "This works better as a one-off helper than an always-on job.",
    "not-a-loop": "This is not a good fit to automate. Here is a simpler way.",
}
_DANGER = {
    "vague_done": "It is not yet clear what finished means, so we need to pin that down.",
    "unsafe_external_action": "It could send, post, publish, delete, or spend, so it should ask you first.",
    "review_debt_machine": "It could create more to review than you can keep up with, so we should cap it.",
}

def _level(code, table, fallback):
    token = (str(code).strip().split() or [""])[0]
    digit = token[1:2] if token[:1].upper() in ("R", "L") else ""
    return table.get(digit, fallback)

def plain_archetype(name):
    key = str(name).lower().replace(" loop", "").strip()
    return _ARCHETYPE.get(key, "a job AI runs for you on repeat")

def plain_risk(code):
    return _level(code, _RISK, "it may take actions, so review the first run carefully")

def plain_maturity(code):
    return _level(code, _MATURITY, "start by running it yourself before automating")

def plain_verdict(code):
    return _VERDICT.get(str(code).strip().lower(), "Let us look at whether this is a good fit.")

def plain_danger(flag):
    return _DANGER.get(str(flag).strip().lower(),
                       "There is a risk here worth a closer look before automating.")

def plainify(result):
    result = result or {}
    flags = result.get("flags") or []
    return {
        "what_it_does": plain_archetype(result.get("archetype", "")),
        "careful_because": plain_risk(result.get("risk", "")),
        "how_it_starts": plain_maturity(result.get("maturity", "")),
        "watch_for": [plain_danger(f) for f in flags],
    }

def blocker_questions(result):
    """Return beginner-safe questions, limited to actual blockers."""
    result = result or {}
    questions = []
    source = str(result.get("source") or "")
    done = str(result.get("done") or "")
    flags = set(result.get("flags") or [])
    raw = " ".join(str(x) for x in [source, done, *flags]).lower()

    if "unknown source" in source.lower():
        questions.append("What should I inspect first?")
    if "not specified" in done.lower():
        questions.append("What would make one run count as finished, and how should I check it?")
    if "unsafe_external_action" in flags:
        questions.append("Which actions must I ask you to approve before I take them?")
    elif not questions:
        questions.append("What should I hand back for your decision?")
    if "approval" in raw and not any("approve" in q for q in questions):
        questions.append("Which decisions need your approval?")
    return questions[:3]

def beginner_packet(goal):
    """Build a plain-language beginner packet for golden prompt tests."""
    import loop_onboard

    mapped = loop_onboard.map_loop(goal)
    plain = plainify(mapped)
    questions = blocker_questions(mapped)
    return {
        "summary": plain["what_it_does"],
        "careful_because": plain["careful_because"],
        "first_run": "I will run the first version safely, with checkpoints.",
        "questions": questions,
        "on_my_own": [
            "map the job",
            "create the first-run checkpoint",
            "inspect the source you provide",
            "capture evidence",
            "return an output packet with a recommendation",
        ],
        "checks_with_you_first": [
            "anything that sends, posts, publishes, deletes, spends, or changes something outside the draft"
        ],
        "first_run_instructions": [
            "freeze the source before acting",
            "run only the allowed read-only or local draft steps",
            "stop if approval, access, or judgment is missing",
            "write evidence and verifier results before closing the run",
        ],
        "runnable_command": "python3 shared/scripts/checkpoint_run.py init --spec spec.md --out .loop-kit/<loop-slug>",
        "output_packet": [
            "what I inspected",
            "what passed or failed",
            "what evidence I captured",
            "what needs your approval",
            "whether this should run again",
        ],
    }

if __name__ == "__main__":
    import json, sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    import loop_onboard
    query = sys.argv[1] if len(sys.argv) > 1 else "review my drafts before publishing"
    print(json.dumps(beginner_packet(query), indent=2))
