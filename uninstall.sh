#!/usr/bin/env bash
# uninstall.sh -- remove loop-kit from Claude Code and/or Codex skills dirs
#
# Usage:
#   bash uninstall.sh [--runtime codex|claude|both]
#
# Defaults to --runtime both.

set -euo pipefail

RUNTIME="both"

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
    *)
      echo "Unknown argument: $1" >&2
      echo "Usage: $0 [--runtime codex|claude|both]" >&2
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

remove_kit() {
  local target_base="$1"
  local kit_dest="${target_base}/loop-kit"

  if [[ -d "${kit_dest}" ]]; then
    rm -rf "${kit_dest}"
    echo "  Removed: ${kit_dest}"
  else
    echo "  Not found (skipping): ${kit_dest}"
  fi
}

echo "loop-kit uninstall  (runtime: ${RUNTIME})"
echo "----------------------------------------------"

if [[ "$RUNTIME" == "claude" || "$RUNTIME" == "both" ]]; then
  echo "Uninstalling claude..."
  remove_kit "${HOME}/.claude/skills"
fi

if [[ "$RUNTIME" == "codex" || "$RUNTIME" == "both" ]]; then
  echo "Uninstalling codex..."
  remove_kit "${HOME}/.codex/skills"
fi

echo "----------------------------------------------"
echo "Done."
