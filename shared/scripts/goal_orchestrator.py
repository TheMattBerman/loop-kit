#!/usr/bin/env python3
"""Create durable Goal Orchestrator cycle artifacts from a JSON input file."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "shared" / "library"
sys.path.insert(0, str(LIB))

from goal_orchestrator import build_goal_cycle, load_cycle_input, write_cycle_artifacts


def main():
    parser = argparse.ArgumentParser(description="Build a local Goal Orchestrator cycle packet.")
    parser.add_argument("input_json", help="JSON file with objective, optional success_criteria, constraints, and result_report")
    parser.add_argument("--output-dir", required=True, help="Directory where cycle artifacts should be written")
    args = parser.parse_args()

    payload = load_cycle_input(args.input_json)
    cycle = build_goal_cycle(
        payload["objective"],
        result_report_text=payload.get("result_report", ""),
        success_criteria=payload.get("success_criteria"),
        constraints=payload.get("constraints"),
        cycle_id=payload.get("cycle_id"),
    )
    files = write_cycle_artifacts(cycle, args.output_dir)
    print(json.dumps({"cycle_id": cycle["cycle_id"], "decision": cycle["decision"], "files": files}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
