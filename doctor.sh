#!/usr/bin/env bash
# doctor.sh -- health-check loop-kit
#
# Checks:
#   1. python3 is available
#   2. pytest suite passes  (python3 -m pytest tests/ -q)
#   3. audit_kit passes     (python3 shared/scripts/audit_kit.py)
#   4. runtime cases pass   (python3 shared/scripts/audit_runtime_cases.py)
#   5. V2 eval suites pass
#   6. V3-A connector/evidence/safety eval suites pass
#   7. V3-B graduation/schedule-readiness eval suites pass
#   8. V4 sandbox controlled recurrence eval suites pass
#   9. V5 goal orchestrator eval suites pass
#
# Exits 0 on full PASS, non-zero on any failure.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "${REPO_ROOT}"

PASS=true

echo "loop-kit doctor"
echo "----------------------------------------------"

# 1. python3 check
if command -v python3 >/dev/null 2>&1; then
  PY_VER="$(python3 --version 2>&1)"
  echo "[OK] python3 found: ${PY_VER}"
else
  echo "[FAIL] python3 not found in PATH"
  PASS=false
fi

run_audit() {
  local label="$1"
  local script="$2"
  if [[ "$PASS" == "true" ]]; then
    echo ""
    echo "Running ${script} ..."
    if python3 "shared/scripts/${script}"; then
      echo "[OK] ${label} passed"
    else
      echo "[FAIL] ${label} failed"
      PASS=false
    fi
  fi
}

# 2. pytest
if [[ "$PASS" == "true" ]]; then
  echo ""
  echo "Running pytest tests/ ..."
  if python3 -m pytest tests/ -q; then
    echo "[OK] pytest passed"
  else
    echo "[FAIL] pytest failed"
    PASS=false
  fi
fi

# 3. audit_kit
if [[ "$PASS" == "true" ]]; then
  echo ""
  echo "Running audit_kit.py ..."
  if python3 shared/scripts/audit_kit.py; then
    echo "[OK] audit_kit passed"
  else
    echo "[FAIL] audit_kit failed"
    PASS=false
  fi
fi

# 4. runtime golden cases
if [[ "$PASS" == "true" ]]; then
  echo ""
  echo "Running audit_runtime_cases.py ..."
  if python3 shared/scripts/audit_runtime_cases.py; then
    echo "[OK] runtime golden cases passed"
  else
    echo "[FAIL] runtime golden cases failed"
    PASS=false
  fi
fi

run_audit "conversation cases" "audit_conversation_cases.py"
run_audit "design cases" "audit_design_cases.py"
run_audit "advanced improvement cases" "audit_advanced_improvement_cases.py"
run_audit "operator runtime cases" "audit_operator_runtime_cases.py"
run_audit "connector policy cases" "audit_connector_policy.py"
run_audit "security cases" "audit_security_cases.py"
run_audit "connector adapter cases" "audit_connector_adapters.py"
run_audit "approval artifact cases" "audit_approval_artifacts.py"
run_audit "snapshot integrity cases" "audit_snapshot_integrity.py"
run_audit "no scheduler cases" "audit_no_scheduler.py"
run_audit "graduation cases" "audit_graduation_cases.py"
run_audit "schedule proposal cases" "audit_schedule_proposals.py"
run_audit "controlled recurrence cases" "audit_controlled_recurrence.py"
run_audit "goal orchestrator cases" "audit_goal_orchestrator.py"

echo ""
echo "----------------------------------------------"
if [[ "$PASS" == "true" ]]; then
  echo "PASS"
  exit 0
else
  echo "FAIL"
  exit 1
fi
