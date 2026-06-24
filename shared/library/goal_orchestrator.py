"""Goal orchestration for local agentic build/review/next-goal cycles."""

import json
import re
from pathlib import Path

from source_safety import stable_id


PROHIBITED_ACTIONS = [
    "install a real scheduler",
    "create cron jobs",
    "create hosted monitors",
    "create background jobs",
    "perform connector writes",
    "push",
    "publish",
    "deploy",
    "send",
    "merge",
    "delete",
    "spend",
]


def _sentences(text):
    parts = re.split(r"[.;\n]+", str(text or ""))
    return [part.strip(" -") for part in parts if part.strip(" -")]


def _contains_any(text, terms):
    haystack = str(text or "").lower()
    return any(str(term).lower() in haystack for term in terms)


def _goal_terms(objective):
    words = re.findall(r"[a-z0-9][a-z0-9_-]{3,}", str(objective or "").lower())
    stop = {
        "that",
        "this",
        "with",
        "from",
        "into",
        "should",
        "until",
        "without",
        "system",
        "build",
        "goal",
        "loop",
        "loops",
        "agent",
        "agents",
    }
    terms = []
    for word in words:
        if word not in stop and word not in terms:
            terms.append(word)
    return terms[:8]


def classify_objective(objective):
    text = str(objective or "").lower()
    return {
        "scheduler_setup": _contains_any(text, ["scheduler", "schedule", "cron", "recurring", "cadence"]),
        "connector_setup": _contains_any(text, ["connector", "gmail", "slack", "drive", "github", "authorization", "auth"]),
        "external_action": _contains_any(text, ["send", "publish", "deploy", "merge", "delete", "spend", "bill"]),
    }


def derive_success_criteria(objective, supplied=None):
    supplied = [str(item).strip() for item in (supplied or []) if str(item).strip()]
    if supplied:
        criteria = supplied[:]
    else:
        criteria = [
            "Original objective is preserved verbatim in every worker, reviewer, and next-goal packet.",
            "Worker packet has measurable success criteria and an evidence checklist.",
            "Reviewer packet evaluates evidence before accepting completion.",
            "Result report is parsed into pass, fail, partial, blocked, or needs_fix.",
            "Next-goal prompt is produced unless every success criterion is proven complete.",
        ]
    classification = classify_objective(objective)
    if classification["scheduler_setup"]:
        criteria.append("Scheduler setup remains user-owned; the kit gives instructions and evidence requirements without installing schedules.")
    if classification["connector_setup"]:
        criteria.append("Connector setup remains user-owned; the kit names authorization steps without secretly connecting tools.")
    if classification["external_action"]:
        criteria.append("External actions remain approval-gated and are not executed by the orchestrator.")
    return criteria


def make_evidence_checklist(criteria):
    return [
        {
            "criterion_id": f"criterion-{index + 1:02d}",
            "criterion": criterion,
            "required_evidence": [
                "changed file or artifact path",
                "command output or reviewer finding",
                "explicit pass/fail statement",
            ],
        }
        for index, criterion in enumerate(criteria)
    ]


def make_worker_prompt(objective, criteria, constraints=None):
    constraints = constraints or []
    lines = [
        "Goal Orchestrator worker packet",
        "",
        "Original objective:",
        str(objective).strip(),
        "",
        "Success criteria:",
    ]
    lines.extend(f"- {criterion}" for criterion in criteria)
    lines.extend(
        [
            "",
            "Boundaries:",
            "- Preserve the original objective; do not optimize for a narrower subtask.",
            "- Create durable artifacts and cite evidence.",
            "- Do not perform real scheduler installation, connector writes, push, publish, deploy, send, merge, delete, or spend.",
        ]
    )
    lines.extend(f"- {constraint}" for constraint in constraints)
    lines.extend(
        [
            "",
            "Required result report:",
            "## Result",
            "pass / partial / fail / blocked",
            "",
            "## Evidence",
            "",
            "## Criteria Status",
            "",
            "## Remaining Risks",
            "",
            "## Recommendation",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def make_reviewer_prompt(objective, criteria):
    lines = [
        "Goal Orchestrator reviewer packet",
        "",
        "Original objective:",
        str(objective).strip(),
        "",
        "Review stance:",
        "- Verify the result against the original objective, not just the worker's narrowed scope.",
        "- Treat missing, indirect, or weak evidence as not complete.",
        "- Check prohibited scheduler, connector, and external-action boundaries.",
        "",
        "Criteria to verify:",
    ]
    lines.extend(f"- {criterion}" for criterion in criteria)
    lines.extend(
        [
            "",
            "Reviewer output:",
            "## Verdict",
            "pass / needs_fix / blocked",
            "",
            "## Evidence Checked",
            "",
            "## Missing Or Weak Evidence",
            "",
            "## Next Required Goal",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def parse_result_report(report_text):
    text = str(report_text or "")
    lower = text.lower()
    if re.search(r"result\s*[:\n]\s*pass\b", lower) or "\npass\n" in lower:
        result = "pass"
    elif re.search(r"result\s*[:\n]\s*partial\b", lower):
        result = "partial"
    elif re.search(r"result\s*[:\n]\s*blocked\b", lower):
        result = "blocked"
    elif re.search(r"result\s*[:\n]\s*fail(?:ed)?\b", lower):
        result = "fail"
    else:
        result = "needs_fix"
    evidence = []
    for line in _sentences(text):
        if line.lower() in {"result", "evidence", "criteria status", "remaining risks", "recommendation"}:
            continue
        if line.lower() in {"pass", "partial", "fail", "blocked", "needs_fix"}:
            continue
        evidence.append(line)
    prohibited_claims = [action for action in PROHIBITED_ACTIONS if action in lower]
    return {
        "result": result,
        "evidence_lines": evidence[:12],
        "prohibited_claims": prohibited_claims,
        "mentions_scheduler_installed": _contains_any(lower, ["installed scheduler", "created cron", "created a cron", "created hosted monitor"]),
        "mentions_connector_authorized": _contains_any(lower, ["authorized gmail", "connected slack", "connected drive", "connected github"]),
    }


def _criterion_proven(criterion, parsed_report):
    text = " ".join(parsed_report.get("evidence_lines", [])).lower()
    criterion_terms = [term for term in _goal_terms(criterion) if len(term) > 4]
    if not criterion_terms:
        return bool(parsed_report.get("evidence_lines"))
    return all(term in text for term in criterion_terms[:3])


def decide_next_action(objective, criteria, parsed_report, result_report_text=""):
    failures = []
    classification = classify_objective(objective)
    report_text = str(result_report_text or "").lower()
    weak = [
        criterion
        for criterion in criteria
        if parsed_report["result"] == "pass" and not _criterion_proven(criterion, parsed_report)
    ]
    objective_terms = _goal_terms(objective)
    missing_terms = [term for term in objective_terms[:5] if term not in report_text]
    if missing_terms and weak:
        failures.append("original objective not fully evidenced")
    if parsed_report["result"] in {"partial", "fail", "blocked", "needs_fix"}:
        failures.append(f"worker result is {parsed_report['result']}")
    if parsed_report["prohibited_claims"]:
        failures.append("report includes prohibited action claims")
    if parsed_report["mentions_scheduler_installed"]:
        failures.append("scheduler setup must remain user-owned")
    if parsed_report["mentions_connector_authorized"]:
        failures.append("connector authorization must remain user-owned")
    if weak:
        failures.append("one or more success criteria lack direct evidence")
    if failures:
        verdict = "blocked" if parsed_report["result"] == "blocked" else "needs_fix"
    else:
        verdict = "pass"
    setup_instructions = []
    if classification["scheduler_setup"]:
        setup_instructions.extend(
            [
                "User-owned scheduler setup: choose the scheduler, install it outside Loop Kit, run a dry run, and paste the run ledger back for review.",
                "Loop Kit may validate schedule-readiness evidence, but it must not install cron, hosted monitors, or background jobs.",
            ]
        )
    if classification["connector_setup"]:
        setup_instructions.extend(
            [
                "User-owned connector setup: authorize the connector in the host tool, capture the access/scope evidence, and paste a read-only snapshot back for review.",
                "Loop Kit may validate connector-readiness evidence, but it must not secretly authorize or write through connected tools.",
            ]
        )
    return {
        "verdict": verdict,
        "complete": verdict == "pass",
        "failures": failures,
        "setup_instructions": setup_instructions,
    }


def make_next_goal_prompt(objective, criteria, decision):
    if decision["complete"]:
        return "Original objective is complete. No next-goal prompt required.\n"
    lines = [
        "/goal Continue the Goal Orchestrator cycle.",
        "",
        "Original objective:",
        str(objective).strip(),
        "",
        "Fix or complete these gaps:",
    ]
    lines.extend(f"- {failure}" for failure in decision["failures"])
    lines.extend(
        [
            "",
            "Success criteria still apply:",
        ]
    )
    lines.extend(f"- {criterion}" for criterion in criteria)
    if decision["setup_instructions"]:
        lines.extend(["", "User-owned setup instructions:"])
        lines.extend(f"- {instruction}" for instruction in decision["setup_instructions"])
    lines.extend(
        [
            "",
            "Return a result report with evidence for every criterion. Do not claim completion from a narrower subtask.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def build_goal_cycle(objective, result_report_text="", success_criteria=None, constraints=None, cycle_id=None):
    criteria = derive_success_criteria(objective, supplied=success_criteria)
    parsed = parse_result_report(result_report_text)
    decision = decide_next_action(objective, criteria, parsed, result_report_text=result_report_text)
    cycle = {
        "cycle_id": cycle_id or stable_id("goal-cycle", objective),
        "original_objective": str(objective).strip(),
        "success_criteria": criteria,
        "worker_kickoff_prompt": make_worker_prompt(objective, criteria, constraints=constraints),
        "reviewer_prompt": make_reviewer_prompt(objective, criteria),
        "result_report": parsed,
        "evidence_checklist": make_evidence_checklist(criteria),
        "decision": decision,
        "next_goal_prompt": make_next_goal_prompt(objective, criteria, decision),
    }
    return cycle


def write_cycle_artifacts(cycle, output_dir):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    files = {
        "original-objective.md": cycle["original_objective"] + "\n",
        "success-criteria.json": json.dumps(cycle["success_criteria"], indent=2, sort_keys=True) + "\n",
        "worker-kickoff.md": cycle["worker_kickoff_prompt"],
        "reviewer-prompt.md": cycle["reviewer_prompt"],
        "result-report.json": json.dumps(cycle["result_report"], indent=2, sort_keys=True) + "\n",
        "evidence-checklist.json": json.dumps(cycle["evidence_checklist"], indent=2, sort_keys=True) + "\n",
        "decision.json": json.dumps(cycle["decision"], indent=2, sort_keys=True) + "\n",
        "next-goal-prompt.md": cycle["next_goal_prompt"],
    }
    written = {}
    for name, content in files.items():
        path = output / name
        path.write_text(content)
        written[name] = str(path)
    return written


def load_cycle_input(path):
    return json.loads(Path(path).read_text())
