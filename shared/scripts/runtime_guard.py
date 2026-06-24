#!/usr/bin/env python3
"""CLI wrapper for runtime policy checks."""

import argparse
import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "library"
sys.path.insert(0, str(LIB))

from runtime_policy import evaluate_action, evaluate_close


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    action = sub.add_parser("action")
    action.add_argument("actions", nargs="+")
    action.add_argument("--approval-artifact")

    close = sub.add_parser("close")
    close.add_argument("--terminal-state", required=True)
    close.add_argument("--evidence", action="append", default=[])
    close.add_argument("--verifier-result", action="append", default=[])
    close.add_argument("--no-op-reason")
    close.add_argument("--action", action="append", default=[])
    close.add_argument("--approval-artifact")
    close.add_argument("--schedule-recommendation")
    close.add_argument("--review-gate-required", action="store_true")
    close.add_argument("--review-gate-passed", action="store_true")

    args = parser.parse_args(argv)
    if args.cmd == "action":
        result = evaluate_action(args.actions, args.approval_artifact)
    else:
        verifier_results = [{"passed": v.lower() in {"pass", "passed", "true", "ok"}} for v in args.verifier_result]
        result = evaluate_close(
            args.terminal_state,
            evidence=args.evidence,
            verifier_results=verifier_results,
            no_op_reason=args.no_op_reason,
            actions=args.action,
            approval_artifact=args.approval_artifact,
            review_gate_required=args.review_gate_required,
            review_gate_passed=args.review_gate_passed,
            schedule_recommendation=args.schedule_recommendation,
        )
    print(json.dumps(result, indent=2))
    return 0 if result.get("allowed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
