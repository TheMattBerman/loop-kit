"""Source-safety quarantine helpers for untrusted connector content."""

import hashlib
import re


SECRET_RE = re.compile(r"(api[_-]?key|token|secret|password)\s*[:=]\s*([A-Za-z0-9_\-]{8,})", re.I)
TOOL_ACTION_RE = re.compile(
    r"\b(send|post|publish|deploy|merge|delete|spend|bill|curl|ssh|rm\s+-rf|git\s+push|gh\s+pr\s+merge)\b",
    re.I,
)
SOURCE_INSTRUCTION_RE = re.compile(
    r"\b(ignore|override|disregard|follow these instructions|system prompt|developer message|"
    r"approval granted|has already been approved|approved by source|approval_id|tool_call|function_call|run this command|execute)\b",
    re.I,
)


def stable_id(prefix, text):
    digest = hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def redact_secrets(text):
    return SECRET_RE.sub(lambda match: f"{match.group(1)}=<redacted>", str(text or ""))


def quarantine_source_text(text):
    """Return quarantine metadata for untrusted source content.

    Source content is evidence, not instruction. This helper detects instruction-like
    text, tool-action requests, and secret-like values without echoing secret values.
    """
    raw = str(text or "")
    redacted = redact_secrets(raw)
    source_instruction = bool(SOURCE_INSTRUCTION_RE.search(raw))
    tool_action = bool(TOOL_ACTION_RE.search(raw))
    secret = bool(SECRET_RE.search(raw))
    blocked = source_instruction or tool_action or secret
    refs = []
    if blocked:
        refs.append(stable_id("quarantine", redacted))
    return {
        "blocked": blocked,
        "source_instruction_quarantined": source_instruction,
        "tool_action": tool_action,
        "secret_leak": secret,
        "redacted_text": redacted,
        "quarantine_refs": refs,
        "evidence_id": refs[0] if refs else None,
    }
