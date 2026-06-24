from datetime import datetime, timezone
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from approval_artifacts import validate_approval_artifact


def test_approval_artifact_scopes_to_action_plan():
    plan = {
        "run_id": "run-1",
        "connector": "fake_gmail_thread",
        "action_type": "send",
        "target": "thread-1",
        "payload_hash": "hash-1",
        "source_snapshot_id": "snap-1",
    }
    artifact = {
        "approval_id": "ap-1",
        **plan,
        "approved_by": "operator",
        "approved_at": "2026-06-24T11:00:00+00:00",
        "expires_at": "2026-06-24T13:00:00+00:00",
        "single_use": True,
    }
    result = validate_approval_artifact(artifact, plan, now=datetime(2026, 6, 24, 12, 0, 0, tzinfo=timezone.utc))
    assert result["approved"]
    wrong = dict(artifact)
    wrong["action_type"] = "read"
    blocked = validate_approval_artifact(wrong, plan, now=datetime(2026, 6, 24, 12, 0, 0, tzinfo=timezone.utc))
    assert not blocked["approved"]
