#!/usr/bin/env python3
"""Create and close first-run checkpoint folders."""

import argparse
import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "library"
sys.path.insert(0, str(LIB))

from checkpoints import close_checkpoint, init_checkpoint
from spec_schema import validate_spec


def _verifier_results(items):
    results = []
    for item in items or []:
        label, _, status = item.partition(":")
        results.append({"type": label or "manual", "passed": status.lower() in {"pass", "passed", "ok", "true"}})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    preflight = sub.add_parser("preflight")
    preflight.add_argument("--spec", required=True)

    init = sub.add_parser("init")
    init.add_argument("--spec", required=True)
    init.add_argument("--out", required=True)

    close = sub.add_parser("close")
    close.add_argument("--run", required=True)
    close.add_argument("--verdict", required=True)
    close.add_argument("--evidence", action="append", default=[])
    close.add_argument("--verifier-result", action="append", default=[])
    close.add_argument("--no-op-reason")
    close.add_argument("--action", action="append", default=[])
    close.add_argument("--approval-artifact")
    close.add_argument("--review-gate-required", action="store_true")
    close.add_argument("--review-gate-passed", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "preflight":
            result = validate_spec(Path(args.spec).read_text())
            print(json.dumps({k: v for k, v in result.items() if k != "spec"}, indent=2))
            return 0 if result["valid"] else 1
        if args.cmd == "init":
            result = init_checkpoint(args.spec, args.out)
        else:
            result = close_checkpoint(
                args.run,
                args.verdict,
                evidence=args.evidence,
                verifier_results=_verifier_results(args.verifier_result),
                no_op_reason=args.no_op_reason,
                actions=args.action,
                approval_artifact=args.approval_artifact,
                review_gate_required=args.review_gate_required,
                review_gate_passed=args.review_gate_passed,
            )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
