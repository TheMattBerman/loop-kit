#!/usr/bin/env bash
# compare-baseline.sh
# "Still beats vanilla" gate: runs audit_kit.py over golden/cases.json and
# prints a one-line PASS/FAIL summary.
#
# This is the AUTOMATED half of the baseline comparison. It confirms that all
# golden cases still pass after any change to loop_onboard.py, design_judge.py,
# or golden/cases.json. It does NOT run a full LLM A/B test -- that is a
# documented manual step described in verdicts/README.md.
#
# Usage:
#   bash scripts/compare-baseline.sh
#   Exit code 0 = all golden cases pass (kit beats vanilla on known examples)
#   Exit code 1 = one or more golden cases regressed

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AUDIT="$REPO_ROOT/shared/scripts/audit_kit.py"

output=$(python3 "$AUDIT" 2>&1)
exit_code=$?

if [ "$exit_code" -eq 0 ]; then
  echo "PASS -- $output"
else
  echo "FAIL -- $output"
fi

exit "$exit_code"
