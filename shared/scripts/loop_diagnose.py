#!/usr/bin/env python3
"""Advanced loop diagnosis with concrete missing-field improvements."""

import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "library"
sys.path.insert(0, str(LIB))

from spec_schema import validate_spec


IMPROVEMENTS = {
    "source_of_truth": "Add a named source of truth the run can inspect before it starts.",
    "done_criteria": "Replace soft success wording with a concrete done condition and threshold.",
    "verification_method": "Add a deterministic check, such as a command, file assertion, or JSON field assertion.",
    "approval_boundary": "Add the actions that require approval before the run can take them.",
    "hard_stops": "Add a hard stop for time, items, attempts, spend, or repeated failures.",
    "no_op_condition": "Add what counts as nothing to do and what packet should be returned.",
    "output_packet": "Specify the exact evidence packet the run must return.",
    "first_manual_dry_run": "Require one supervised first run before any schedule decision.",
    "tools_and_permissions": "List allowed tools plus forbidden and approval-required actions.",
    "state_location": "Name the state file or say no state is needed for a one-off run.",
    "run_artifacts": "List the files or evidence IDs every run must produce.",
    "maker_checker_split": "Add a checker who is different from the maker for consequential or subjective output.",
    "schedule_decision": "State that scheduling is only safe to consider after a manual pass with evidence.",
    "approval_artifact": "Require an approval artifact before any external or customer-facing action.",
}

PATCH_VALUES = {
    "source_of_truth": "source_of_truth: <named file, queue, repo path, export, or URL the run must inspect first>",
    "done_criteria": "done_criteria: Each item receives an approve/fix/reject verdict and an evidence id.",
    "verification_method": "verification_method: Run a deterministic command/file/JSON check and record pass/fail output.",
    "approval_boundary": "approval_boundary: Read-only actions are allowed; send/post/publish/deploy/merge/delete/spend require approval.",
    "hard_stops": "hard_stops: Stop after 10 items, 30 minutes, 2 failed verifier attempts, or any missing approval.",
    "no_op_condition": "no_op_condition: If no source items changed, close no_op with a short reason and evidence of the empty source.",
    "output_packet": "output_packet: Return output-packet.md with verdicts, evidence ids, verifier results, blockers, and next decision.",
    "first_manual_dry_run": "first_manual_dry_run: Required before any schedule recommendation.",
    "tools_and_permissions": "tools_and_permissions: Allowed read-only inspection and local file writes; approval required for external actions.",
    "state_location": "state_location: .loop-kit/<loop-slug>/STATE.md, or none if this loop has no recurrence/state.",
    "run_artifacts": "run_artifacts: checkpoint.json, source-freeze.md, output-packet.md, blockers.md, approval-request.yaml.",
    "maker_checker_split": "maker_checker_split: Maker drafts the output; a separate checker reviews evidence before approval.",
    "schedule_decision": "schedule_decision: Only safe_to_consider_scheduling after manual_pass, evidence, review gate, and required approval artifact.",
    "approval_artifact": "approval_artifact: approval-request.yaml with approver, approved action, timestamp, and scope.",
}


def diagnose(spec_or_text):
    validation = validate_spec(spec_or_text)
    missing_fields = list(validation["missing"])
    vague_fields = list(validation["vague"])
    improvements = []
    patches = []
    for field in missing_fields + vague_fields:
        if field in IMPROVEMENTS and IMPROVEMENTS[field] not in improvements:
            improvements.append(IMPROVEMENTS[field])
        if field in PATCH_VALUES:
            patches.append({"field": field, "replace_with": PATCH_VALUES[field]})
    return {
        "verdict": "go" if validation["valid"] else "fix-then-go",
        "missing_fields": missing_fields,
        "vague_fields": vague_fields,
        "expanded_required": validation["expanded_required"],
        "improvements": improvements,
        "patches": patches,
    }


def main(argv=None):
    argv = list(argv or sys.argv[1:])
    data = Path(argv[0]).read_text() if argv else sys.stdin.read()
    result = diagnose(data)
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "go" else 1


if __name__ == "__main__":
    raise SystemExit(main())
