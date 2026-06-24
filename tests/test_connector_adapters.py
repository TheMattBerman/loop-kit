import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from connectors import ADAPTERS, make_adapter
from fake_providers import FakeProvider


def test_five_connector_classes_have_complete_manifests():
    assert len(ADAPTERS) >= 5
    required = {
        "name",
        "version",
        "mode",
        "source_types",
        "allowed_actions",
        "draft_allowed_actions",
        "approval_required_actions",
        "forbidden_actions",
        "auth_required",
        "missing_auth_behavior",
        "snapshot_method",
        "evidence_method",
        "source_trust",
        "prompt_injection_policy",
        "side_effect_ledger_path",
    }
    for name in ADAPTERS:
        manifest = make_adapter(name).manifest()
        assert required <= set(manifest), name
        assert manifest["source_trust"] == "untrusted_source"


def test_local_file_adapter_freezes_snapshot_and_evidence(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("ordinary source\n")
    adapter = make_adapter("local_file", provider_root=tmp_path / "ledger")
    result = adapter.freeze_source(str(source), run_dir=tmp_path / "run")
    assert result["status"] == "ok"
    snapshot = result["snapshot"]
    assert snapshot["snapshot_id"]
    assert (tmp_path / "run" / "source-snapshot.json").exists()
    read = adapter.read(snapshot, run_dir=tmp_path / "run")
    assert read["evidence"]["snapshot_id"] == snapshot["snapshot_id"]
    assert (tmp_path / "run" / "evidence.jsonl").exists()
    assert not FakeProvider(tmp_path / "ledger").forbidden_side_effects()


def test_missing_auth_blocks_fake_provider():
    adapter = make_adapter("fake_gmail_thread")
    result = adapter.freeze_source("thread-1")
    assert result["status"] == "blocked"
    assert "fake_gmail_thread:auth" in result["blocker"]


def test_action_plan_never_executes_external_write(tmp_path):
    adapter = make_adapter("local_file", provider_root=tmp_path / "ledger")
    plan = adapter.prepare_action(
        {
            "run_id": "run-1",
            "action_type": "publish",
            "target": "target",
            "payload": {"body": "draft"},
            "source_snapshot_id": "snap-1",
        }
    )
    assert plan["status"] == "blocked"
    assert "approval" in plan["reason"] or "forbidden" in plan["reason"]
    assert not FakeProvider(tmp_path / "ledger").forbidden_side_effects()


def test_draft_action_creates_only_draft_ledger(tmp_path):
    adapter = make_adapter("fake_drive_doc", provider_root=tmp_path / "ledger", auth_available=True)
    plan = adapter.prepare_action(
        {
            "run_id": "run-1",
            "action_type": "draft",
            "target": "doc-1",
            "payload": {"body": "draft"},
            "source_snapshot_id": "snap-1",
        }
    )
    assert plan["status"] == "draft_prepared"
    assert (tmp_path / "ledger" / "drafts.jsonl").exists()
    assert not FakeProvider(tmp_path / "ledger").forbidden_side_effects()
