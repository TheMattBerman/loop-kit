"""Evidence packet records for connector snapshots and verifier output."""

import json
from datetime import datetime, timezone
from pathlib import Path

from source_safety import stable_id


REQUIRED_EVIDENCE_FIELDS = [
    "evidence_id",
    "snapshot_id",
    "adapter_name",
    "target",
    "observed_at",
    "operation",
    "expected",
    "actual",
    "passed",
    "artifact_ref",
    "redactions",
    "approval_status",
    "quarantine_refs",
]


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def make_evidence(snapshot, target, operation="read", expected="source readable", actual="source captured", passed=True, artifact_ref="source-snapshot.json", approval_status="not_required"):
    payload = {
        "snapshot_id": snapshot["snapshot_id"],
        "adapter_name": snapshot["adapter_name"],
        "target": str(target),
        "operation": operation,
        "expected": expected,
        "actual": actual,
        "passed": bool(passed),
        "artifact_ref": artifact_ref,
        "redactions": ["source_secret_redacted"] if snapshot.get("content_redacted") else [],
        "approval_status": approval_status,
        "quarantine_refs": snapshot.get("quarantined_source_instruction_ids", []),
    }
    payload["evidence_id"] = stable_id("ev", json.dumps(payload, sort_keys=True))
    payload["observed_at"] = utc_now()
    return payload


def validate_evidence(record):
    missing = [field for field in REQUIRED_EVIDENCE_FIELDS if field not in record]
    return {"valid": not missing, "missing": missing}


def append_evidence(record, run_dir):
    validation = validate_evidence(record)
    if not validation["valid"]:
        raise ValueError("invalid evidence: missing " + ", ".join(validation["missing"]))
    path = Path(run_dir) / "evidence.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return str(path)


def read_evidence(path):
    evidence_path = Path(path)
    if not evidence_path.exists():
        return []
    return [json.loads(line) for line in evidence_path.read_text().splitlines() if line.strip()]
