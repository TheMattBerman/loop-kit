#!/usr/bin/env python3
"""Validate a loop spec with the strong checkpoint schema."""

import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "library"
sys.path.insert(0, str(LIB))

from spec_schema import validate_spec


def main(argv=None):
    argv = list(argv or sys.argv[1:])
    if argv:
        data = Path(argv[0]).read_text()
    else:
        data = sys.stdin.read()
    result = validate_spec(data)
    print(json.dumps({k: v for k, v in result.items() if k != "spec"}, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
