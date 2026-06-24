"""First-run checkpoint store for supervised loop runs."""

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from runtime_policy import evaluate_close
from spec_schema import has_external_action, normalize_spec, requires_expanded_fields, validate_spec


RUN_FILES = [
    "checkpoint.json",
    "source-freeze.md",
    "output-packet.md",
    "blockers.md",
    "approval-request.yaml",
]


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value):
    text = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or "loop").strip())
    text = "-".join(part for part in text.split("-") if part)
    return text or "loop"


def state_required(spec):
    value = str(spec.get("state_location") or "").strip().lower()
    if value and value not in {"none", "n/a", "na", "not needed", "no state"}:
        return True
    trigger = str(spec.get("trigger") or "").lower()
    return any(token in trigger for token in ("daily", "weekly", "monthly", "recurring"))


def _git(args, cwd):
    try:
        completed = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
        if completed.returncode == 0:
            return completed.stdout.strip()
    except OSError:
        pass
    return "unavailable"


def source_freeze_text(cwd):
    branch = _git(["branch", "--show-current"], cwd)
    upstream = _git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd)
    dirty = _git(["status", "--short"], cwd)
    return "\n".join(
        [
            "# Source Freeze",
            f"- captured_at: {utc_now()}",
            f"- branch: {branch}",
            f"- upstream: {upstream}",
            f"- dirty_state: {dirty or 'clean'}",
            "",
        ]
    )


def init_checkpoint(spec_path, out_dir, cwd=None):
    spec_path = Path(spec_path)
    out_dir = Path(out_dir)
    cwd = Path(cwd or Path.cwd())
    spec_text = spec_path.read_text()
    validation = validate_spec(spec_text)
    if not validation["valid"]:
        raise ValueError("invalid spec: " + ", ".join(validation["errors"]))

    spec = normalize_spec(spec_text)
    review_gate_required = requires_expanded_fields(spec)
    approval_artifact_required = review_gate_required or has_external_action(spec)
    loop_id = slugify(spec.get("id") or spec.get("name") or spec_path.stem)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = out_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    out_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(spec_path, out_dir / "spec.md")
    if state_required(spec):
        (out_dir / "STATE.md").write_text("# Loop State\n\n- last_run: none\n")

    checkpoint = {
        "run_id": run_id,
        "loop_id": loop_id,
        "started_at": utc_now(),
        "ended_at": None,
        "terminal_state": None,
        "source_freeze": "source-freeze.md",
        "commands_or_actions_attempted": [],
        "evidence": [],
        "verifier_results": [],
        "blockers": [],
        "proposed_changes": [],
        "accepted_changes": [],
        "approval_required": False,
        "approval_artifact": None,
        "review_gate_required": review_gate_required,
        "review_gate_passed": False,
        "approval_artifact_required": approval_artifact_required,
        "next_decision": "run_first_pass",
        "schedule_recommendation": "do_not_schedule",
    }
    (run_dir / "checkpoint.json").write_text(json.dumps(checkpoint, indent=2) + "\n")
    (run_dir / "source-freeze.md").write_text(source_freeze_text(cwd))
    (run_dir / "output-packet.md").write_text("# Output Packet\n\n- status: pending\n")
    (run_dir / "blockers.md").write_text("# Blockers\n\nNone recorded.\n")
    (run_dir / "approval-request.yaml").write_text("approval_required: false\napproval_artifact:\n")
    return {"loop_dir": str(out_dir), "run_dir": str(run_dir), "run_id": run_id, "loop_id": loop_id}


def output_packet_text(checkpoint, no_op_reason=None):
    evidence = checkpoint.get("evidence") or []
    verifier_results = checkpoint.get("verifier_results") or []
    blockers = checkpoint.get("blockers") or []
    lines = [
        "# Output Packet",
        "",
        f"- status: {checkpoint.get('terminal_state') or 'pending'}",
        f"- ended_at: {checkpoint.get('ended_at') or 'pending'}",
        f"- schedule_recommendation: {checkpoint.get('schedule_recommendation') or 'do_not_schedule'}",
        "",
        "## Evidence",
    ]
    if evidence:
        lines.extend(f"- {item}" for item in evidence)
    else:
        lines.append("- none")
    lines.extend(["", "## Verifier Results"])
    if verifier_results:
        for item in verifier_results:
            if isinstance(item, dict):
                label = item.get("type") or item.get("name") or "verifier"
                status = "pass" if item.get("passed") else "fail"
                lines.append(f"- {label}: {status}")
            else:
                lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Blockers"])
    if blockers:
        lines.extend(f"- {item}" for item in blockers)
    elif no_op_reason:
        lines.append(f"- {no_op_reason}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def close_checkpoint(
    run_dir,
    verdict,
    evidence=None,
    verifier_results=None,
    no_op_reason=None,
    actions=None,
    approval_artifact=None,
    review_gate_required=False,
    review_gate_passed=False,
):
    run_dir = Path(run_dir)
    checkpoint_path = run_dir / "checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text())
    effective_review_gate_required = bool(review_gate_required or checkpoint.get("review_gate_required"))
    effective_approval_artifact_required = bool(checkpoint.get("approval_artifact_required"))
    policy = evaluate_close(
        verdict,
        evidence=evidence,
        verifier_results=verifier_results,
        no_op_reason=no_op_reason,
        actions=actions,
        approval_artifact=approval_artifact,
        review_gate_required=effective_review_gate_required,
        review_gate_passed=review_gate_passed,
        approval_artifact_required=effective_approval_artifact_required,
    )
    if not policy["allowed"]:
        raise ValueError("; ".join(policy["failures"]))

    checkpoint.update(
        {
            "ended_at": utc_now(),
            "terminal_state": verdict,
            "evidence": evidence or [],
            "verifier_results": verifier_results or [],
            "commands_or_actions_attempted": actions or [],
            "approval_required": bool(policy["approval_required"]),
            "approval_artifact": approval_artifact,
            "review_gate_required": effective_review_gate_required,
            "review_gate_passed": bool(review_gate_passed),
            "approval_artifact_required": effective_approval_artifact_required,
            "next_decision": "closed",
            "schedule_recommendation": policy["schedule_recommendation"],
        }
    )
    if verdict == "no_op":
        checkpoint["blockers"] = [no_op_reason]
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2) + "\n")
    (run_dir / "output-packet.md").write_text(output_packet_text(checkpoint, no_op_reason=no_op_reason))
    return checkpoint
