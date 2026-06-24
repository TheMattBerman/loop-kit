"""Maker/checker review gate for consequential loop outputs."""


def _truthy(value):
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _items(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def validate_review_packet(packet):
    packet = packet or {}
    maker = str(packet.get("maker") or "").strip()
    checker = str(packet.get("checker") or "").strip()
    requires_second_review = any(
        _truthy(packet.get(key))
        for key in ("consequential", "subjective", "external_action", "customer_or_production")
    )
    evidence_refs = _items(packet.get("evidence_refs"))
    checker_output = str(packet.get("checker_output") or "").strip()
    has_second_review = _truthy(packet.get("second_review_packet")) or bool(checker_output)

    failures = []
    if requires_second_review and not has_second_review:
        failures.append("second review packet required")
    if requires_second_review and maker and checker and maker == checker:
        failures.append("maker and checker must be different")
    if requires_second_review and not checker:
        failures.append("checker required")
    if requires_second_review and not evidence_refs:
        failures.append("checker output must reference evidence")
    if requires_second_review and checker_output and not any(ref in checker_output for ref in evidence_refs):
        failures.append("checker output must cite an evidence ref")

    return {
        "passed": not failures,
        "requires_second_review": requires_second_review,
        "failures": failures,
    }
