"""Source snapshot contract for connector adapter reads."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from source_safety import quarantine_source_text, stable_id


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text):
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def normalize_items(items):
    normalized = []
    quarantines = []
    for item in items:
        text = str(item.get("content", ""))
        quarantine = quarantine_source_text(text)
        if quarantine["quarantine_refs"]:
            quarantines.extend(quarantine["quarantine_refs"])
        normalized.append(
            {
                "id": str(item.get("id") or len(normalized) + 1),
                "target": str(item.get("target") or item.get("id") or "item"),
                "content": quarantine["redacted_text"],
                "metadata": item.get("metadata") or {},
            }
        )
    return normalized, sorted(set(quarantines))


def build_snapshot(adapter_name, source_ref, source_type, items, canonical_uri=None, revision_id_or_etag=None):
    normalized, quarantines = normalize_items(items)
    normalized_text = "\n".join(item["content"] for item in normalized)
    metadata = {
        "adapter_name": adapter_name,
        "source_ref": str(source_ref),
        "source_type": source_type,
        "canonical_uri": canonical_uri or str(source_ref),
        "revision_id_or_etag": revision_id_or_etag or sha256_text(normalized_text)[:16],
        "item_count": len(normalized),
        "trust_level": "untrusted_source",
        "quarantined_source_instruction_ids": quarantines,
    }
    snapshot_id = stable_id("snap", canonical_json({"metadata": metadata, "items": normalized}))
    metadata_sha = sha256_text(canonical_json(metadata))
    snapshot = {
        "snapshot_id": snapshot_id,
        "captured_at": utc_now(),
        "normalized_sha256": sha256_text(normalized_text),
        "metadata_sha256": metadata_sha,
        "content_redacted": bool(quarantines),
        "artifact_ref": "source-snapshot.json",
        **metadata,
        "items": normalized,
    }
    return snapshot


def write_snapshot_artifacts(snapshot, run_dir):
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "source-snapshot.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    normalized = "\n".join(item.get("content", "") for item in snapshot.get("items", []))
    (run_dir / "source-snapshot-normalized.txt").write_text(normalized + ("\n" if normalized else ""))
    return {
        "snapshot_json": str(run_dir / "source-snapshot.json"),
        "normalized": str(run_dir / "source-snapshot-normalized.txt"),
    }


def load_snapshot(path):
    return json.loads(Path(path).read_text())


def verify_snapshot_integrity(snapshot, current_items):
    current = build_snapshot(
        snapshot["adapter_name"],
        snapshot["source_ref"],
        snapshot["source_type"],
        current_items,
        canonical_uri=snapshot.get("canonical_uri"),
        revision_id_or_etag=snapshot.get("revision_id_or_etag"),
    )
    return {
        "passed": current["normalized_sha256"] == snapshot["normalized_sha256"],
        "snapshot_id": snapshot["snapshot_id"],
        "expected_sha256": snapshot["normalized_sha256"],
        "actual_sha256": current["normalized_sha256"],
        "terminal_state": "manual_pass" if current["normalized_sha256"] == snapshot["normalized_sha256"] else "fix_then_rerun",
    }
