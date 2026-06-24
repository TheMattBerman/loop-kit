#!/usr/bin/env python3
"""Validate maker/checker review packet JSON."""

import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "library"
sys.path.insert(0, str(LIB))

from review_gate import validate_review_packet


def main(argv=None):
    argv = list(argv or sys.argv[1:])
    data = Path(argv[0]).read_text() if argv else sys.stdin.read()
    packet = json.loads(data)
    result = validate_review_packet(packet)
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
