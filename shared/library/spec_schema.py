"""Strong loop spec validation for loop-kit.

The validator intentionally stays small and deterministic. It accepts either a
dict or simple Markdown/YAML-ish text with ``key: value`` lines.
"""

import json
import re


MINIMUM_REQUIRED = [
    "source_of_truth",
    "done_criteria",
    "verification_method",
    "approval_boundary",
    "hard_stops",
    "no_op_condition",
    "output_packet",
    "first_manual_dry_run",
]

EXPANDED_REQUIRED = [
    "tools_and_permissions",
    "state_location",
    "run_artifacts",
    "maker_checker_split",
    "schedule_decision",
    "approval_artifact",
]

VAGUE_TERMS = [
    "good",
    "better",
    "until satisfied",
    "as needed",
    "improve",
    "high quality",
    "make it nice",
    "looks right",
    "best effort",
    "done",
]

VAGUE_FIELDS = ["done_criteria", "verification_method"]

EXTERNAL_ACTION_RE = re.compile(
    r"\b(send|post|publish|deploy|merge|delete|spend|bill)(?:s|es|ed|ing)?\b|customer-facing update",
    re.I,
)


def normalize_key(key):
    return str(key).strip().lower().replace("-", "_").replace(" ", "_")


def parse_spec_text(text):
    """Parse JSON or simple key/value Markdown into a normalized spec dict."""
    raw = (text or "").strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return {normalize_key(k): v for k, v in parsed.items()}
    except json.JSONDecodeError:
        pass

    spec = {}
    for line in raw.splitlines():
        stripped = line.strip().strip("-")
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        spec[normalize_key(key)] = value.strip()
    return spec


def normalize_spec(spec_or_text):
    if isinstance(spec_or_text, dict):
        return {normalize_key(k): v for k, v in spec_or_text.items()}
    return parse_spec_text(str(spec_or_text or ""))


def text_blob(spec):
    return " ".join(str(v) for v in spec.values() if v is not None)


def is_blank(value):
    text = str(value or "").strip().lower()
    return text in {"", "none", "n/a", "na", "unknown", "tbd", "todo"}


def has_external_action(spec):
    return bool(EXTERNAL_ACTION_RE.search(text_blob(spec)))


def requires_expanded_fields(spec):
    risk = str(spec.get("risk") or spec.get("risk_level") or "").upper()
    maturity = str(spec.get("maturity") or "").upper()
    scope = str(spec.get("scope") or "").lower()
    return (
        risk.startswith("R3")
        or risk.startswith("R4")
        or maturity.startswith("L3")
        or maturity.startswith("L4")
        or "customer" in scope
        or "production" in scope
        or has_external_action(spec)
    )


def vague_fields(spec):
    vague = []
    for field in VAGUE_FIELDS:
        value = str(spec.get(field) or "").strip().lower()
        if not value:
            continue
        if len(value.split()) < 3:
            vague.append(field)
            continue
        if any(term in value for term in VAGUE_TERMS):
            vague.append(field)
    return vague


def validate_spec(spec_or_text):
    """Return a structured validation result.

    ``valid`` is true only when every required field is present and done/check
    wording is concrete enough for a deterministic first run.
    """
    spec = normalize_spec(spec_or_text)
    required = list(MINIMUM_REQUIRED)
    expanded = requires_expanded_fields(spec)
    if expanded:
        required.extend(EXPANDED_REQUIRED)

    missing = [field for field in required if is_blank(spec.get(field))]
    vague = vague_fields(spec)
    errors = []
    errors.extend(f"missing:{field}" for field in missing)
    errors.extend(f"vague:{field}" for field in vague)

    return {
        "valid": not missing and not vague,
        "verdict": "PASS" if not missing and not vague else "FAIL",
        "spec": spec,
        "required": required,
        "missing": missing,
        "vague": vague,
        "expanded_required": expanded,
        "external_action": has_external_action(spec),
        "errors": errors,
    }
