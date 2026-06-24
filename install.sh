#!/usr/bin/env bash
# install.sh -- install loop-kit into Claude Code and/or Codex skills dirs
#
# Usage:
#   bash install.sh [--runtime codex|claude|both] [--dry-run]
#
# Defaults to --runtime both.
#
# macOS (native bash/zsh) and Linux are supported.
# Windows: run inside WSL only (native Windows paths are not supported).
#
# The kit is copied as a single unit:
#   ~/.claude/skills/loop-kit/   (claude)
#   ~/.codex/skills/loop-kit/    (codex)
#
# skills/ and shared/ travel TOGETHER under loop-kit/ so that the relative
# paths in SKILL.md (e.g. "python3 shared/scripts/loop_onboard.py") resolve
# when the working directory is the installed kit root.

set -euo pipefail

RUNTIME="both"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runtime)
      RUNTIME="$2"
      shift 2
      ;;
    --runtime=*)
      RUNTIME="${1#*=}"
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      echo "Usage: $0 [--runtime codex|claude|both] [--dry-run]" >&2
      exit 1
      ;;
  esac
done

case "$RUNTIME" in
  codex|claude|both) ;;
  *)
    echo "Error: --runtime must be codex, claude, or both (got: $RUNTIME)" >&2
    exit 1
    ;;
esac

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

required_paths=(
  "skills/loop-doctor/SKILL.md"
  "skills/loop-builder/SKILL.md"
  "skills/loop-start/SKILL.md"
  "shared/scripts/loop_onboard.py"
  "shared/scripts/validate_spec.py"
  "shared/scripts/checkpoint_run.py"
  "shared/scripts/audit_connector_adapters.py"
  "shared/scripts/audit_graduation_cases.py"
  "shared/scripts/audit_schedule_proposals.py"
  "shared/scripts/audit_controlled_recurrence.py"
  "shared/scripts/audit_goal_orchestrator.py"
  "shared/scripts/goal_orchestrator.py"
  "shared/library/spec_schema.py"
  "shared/library/checkpoints.py"
  "shared/library/connectors.py"
  "shared/library/source_snapshots.py"
  "shared/library/evidence_packets.py"
  "shared/library/approval_artifacts.py"
  "shared/library/graduation.py"
  "shared/library/schedule_proposals.py"
  "shared/library/controlled_recurrence.py"
  "shared/library/goal_orchestrator.py"
)

verify_layout() {
  local missing=0
  for rel in "${required_paths[@]}"; do
    if [[ ! -e "${REPO_ROOT}/${rel}" ]]; then
      echo "  missing: ${rel}" >&2
      missing=1
    fi
  done
  return "${missing}"
}

copy_kit() {
  local target_base="$1"
  local kit_dest="${target_base}/loop-kit"

  if [[ "${DRY_RUN}" == "true" ]]; then
    echo "  dry-run target: ${kit_dest}"
    echo "  would copy: skills/ shared/ golden/ redteam/ tests/ docs and scripts"
    echo "  verifying source layout..."
    verify_layout
    echo "  skills:  ${kit_dest}/skills/loop-doctor/"
    echo "  skills:  ${kit_dest}/skills/loop-builder/"
    echo "  skills:  ${kit_dest}/skills/loop-start/"
    echo "  shared:  ${kit_dest}/shared/"
    return 0
  fi

  mkdir -p "${kit_dest}"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --exclude '.git' \
      --exclude '.superpowers' \
      --exclude '.pytest_cache' \
      --exclude '__pycache__' \
      --exclude '*.pyc' \
      "${REPO_ROOT}/" "${kit_dest}/"
    echo "  rsync -> ${kit_dest}"
  else
    # Fallback: cp -R (rsync not present)
    cp -R "${REPO_ROOT}/." "${kit_dest}/"
    # Best-effort cleanup of excluded dirs
    rm -rf "${kit_dest}/.git" \
           "${kit_dest}/.superpowers" \
           "${kit_dest}/shared/scripts/__pycache__" 2>/dev/null || true
    echo "  cp -R -> ${kit_dest} (rsync not available; .git/.superpowers removed)"
  fi

  echo "  skills:  ${kit_dest}/skills/loop-doctor/"
  echo "  skills:  ${kit_dest}/skills/loop-builder/"
  echo "  skills:  ${kit_dest}/skills/loop-start/"
  echo "  shared:  ${kit_dest}/shared/"
}

echo "loop-kit install  (runtime: ${RUNTIME})"
if [[ "${DRY_RUN}" == "true" ]]; then
  echo "mode: dry-run"
fi
echo "----------------------------------------------"

if [[ "$RUNTIME" == "claude" || "$RUNTIME" == "both" ]]; then
  echo "Installing for claude..."
  copy_kit "${HOME}/.claude/skills"
fi

if [[ "$RUNTIME" == "codex" || "$RUNTIME" == "both" ]]; then
  echo "Installing for codex..."
  copy_kit "${HOME}/.codex/skills"
fi

echo "----------------------------------------------"
echo "Done."
