"""V3-A connector adapter contract and read-only/draft-only adapters."""

import hashlib
import json
import subprocess
from pathlib import Path

from approval_artifacts import validate_approval_artifact
from evidence_packets import append_evidence, make_evidence
from fake_providers import FakeProvider
from source_snapshots import build_snapshot, write_snapshot_artifacts


APPROVAL_REQUIRED_ACTIONS = [
    "send",
    "post",
    "publish",
    "deploy",
    "merge",
    "delete",
    "spend",
    "bill",
    "customer-facing update",
]

FORBIDDEN_ACTIONS = ["write", "delete", "send", "post", "publish", "deploy", "merge", "spend", "bill"]


def payload_hash(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()


def capability_manifest(name, mode, source_types, allowed_actions=None, draft_allowed_actions=None, auth_required=False):
    return {
        "name": name,
        "version": "v3-a",
        "mode": mode,
        "source_types": source_types,
        "allowed_actions": allowed_actions or ["read", "snapshot"],
        "draft_allowed_actions": draft_allowed_actions or [],
        "approval_required_actions": APPROVAL_REQUIRED_ACTIONS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "auth_required": bool(auth_required),
        "missing_auth_behavior": "blocked",
        "snapshot_method": "deterministic sha256 normalized snapshot",
        "evidence_method": "evidence.jsonl",
        "source_trust": "untrusted_source",
        "prompt_injection_policy": "quarantine_source_instructions",
        "side_effect_ledger_path": "fake-provider-ledgers",
    }


class ConnectorAdapter:
    name = "base"
    mode = "read_only"
    source_types = []
    auth_required = False
    draft_allowed_actions = []

    def __init__(self, provider=None):
        self.provider = provider

    def manifest(self):
        return capability_manifest(
            self.name,
            self.mode,
            self.source_types,
            draft_allowed_actions=self.draft_allowed_actions,
            auth_required=self.auth_required,
        )

    def check_access(self, source_ref):
        if self.auth_required:
            return {"status": "blocked", "missing": f"{self.name}:auth", "source_ref": str(source_ref)}
        return {"status": "ok", "missing": None, "source_ref": str(source_ref)}

    def collect_items(self, source_ref):
        raise NotImplementedError

    def freeze_source(self, source_ref, run_dir=None):
        access = self.check_access(source_ref)
        if access["status"] != "ok":
            return {"status": "blocked", "blocker": access["missing"]}
        items = self.collect_items(source_ref)
        if self.provider:
            self.provider.read(self.name, source_ref, items)
        snapshot = build_snapshot(self.name, source_ref, self.source_types[0], items)
        artifacts = write_snapshot_artifacts(snapshot, run_dir) if run_dir else {}
        return {"status": "ok", "snapshot": snapshot, "artifacts": artifacts}

    def read(self, snapshot, run_dir=None):
        evidence = make_evidence(snapshot, snapshot.get("source_ref"), operation="read")
        if run_dir:
            append_evidence(evidence, run_dir)
        return {"status": "ok", "evidence": evidence}

    def prepare_action(self, action_intent, approval_artifact=None, used_approvals=None):
        action_type = str(action_intent.get("action_type") or "").strip()
        target = str(action_intent.get("target") or "").strip()
        plan = {
            "run_id": action_intent.get("run_id"),
            "connector": self.name,
            "action_type": action_type,
            "target": target,
            "payload_hash": payload_hash(action_intent.get("payload") or {}),
            "source_snapshot_id": action_intent.get("source_snapshot_id"),
            "requires_approval": action_type in APPROVAL_REQUIRED_ACTIONS,
            "approval_artifact_id": (approval_artifact or {}).get("approval_id") if isinstance(approval_artifact, dict) else None,
            "dry_run": True,
            "status": "blocked",
            "reason": "not evaluated",
        }
        manifest = self.manifest()
        if not action_type or action_type not in manifest["allowed_actions"] + manifest["draft_allowed_actions"] + manifest["approval_required_actions"]:
            plan["reason"] = "unknown capability"
            return plan
        if action_type in manifest["forbidden_actions"] and action_type not in manifest["draft_allowed_actions"]:
            plan["reason"] = "capability mismatch or forbidden action"
            return plan
        if action_type in manifest["draft_allowed_actions"]:
            plan["status"] = "draft_prepared"
            plan["reason"] = "local draft artifact only"
            if self.provider:
                self.provider.draft(self.name, target, plan["payload_hash"])
            return plan
        if plan["requires_approval"]:
            approval = validate_approval_artifact(approval_artifact, plan, used_approvals=used_approvals)
            if not approval["approved"]:
                plan["reason"] = "approval required: " + "; ".join(approval["failures"])
                return plan
            plan["reason"] = "approved action plan prepared; execution disabled in V3-A"
            plan["status"] = "approval_valid_but_not_executable"
            return plan
        if action_type in manifest["allowed_actions"]:
            plan["status"] = "allowed_read_only"
            plan["reason"] = "read-only action"
            return plan
        plan["reason"] = "blocked by default"
        return plan


class LocalFileAdapter(ConnectorAdapter):
    name = "local_file"
    source_types = ["local_file"]

    def collect_items(self, source_ref):
        path = Path(source_ref)
        if path.is_dir():
            items = []
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    items.append({"id": str(child.relative_to(path)), "target": str(child), "content": child.read_text(errors="replace")})
            return items
        return [{"id": path.name, "target": str(path), "content": path.read_text(errors="replace") if path.exists() else ""}]


class LocalRepoAdapter(ConnectorAdapter):
    name = "local_repo"
    source_types = ["local_repo"]

    def _git(self, args, cwd):
        completed = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
        return completed.stdout.strip() if completed.returncode == 0 else completed.stderr.strip()

    def collect_items(self, source_ref):
        repo = Path(source_ref)
        status = self._git(["status", "--short", "--branch"], repo)
        log = self._git(["log", "--oneline", "-5"], repo)
        diff_stat = self._git(["diff", "--stat"], repo)
        return [
            {"id": "status", "target": "git status", "content": status},
            {"id": "log", "target": "git log", "content": log},
            {"id": "diff_stat", "target": "git diff --stat", "content": diff_stat},
        ]


class FakeUrlSnapshotAdapter(ConnectorAdapter):
    name = "fake_url"
    source_types = ["url"]

    def collect_items(self, source_ref):
        return [{"id": "url-snapshot", "target": str(source_ref), "content": f"Read-only URL fixture for {source_ref}"}]


class FakeDriveDocAdapter(ConnectorAdapter):
    name = "fake_drive_doc"
    source_types = ["drive_doc"]
    auth_required = True
    draft_allowed_actions = ["draft"]

    def __init__(self, provider=None, auth_available=False):
        super().__init__(provider=provider)
        self.auth_required = not auth_available

    def collect_items(self, source_ref):
        return [{"id": "doc", "target": str(source_ref), "content": "Fake document body for snapshot only."}]


class FakeGmailThreadAdapter(ConnectorAdapter):
    name = "fake_gmail_thread"
    source_types = ["gmail_thread"]
    auth_required = True
    draft_allowed_actions = ["draft"]

    def __init__(self, provider=None, auth_available=False):
        super().__init__(provider=provider)
        self.auth_required = not auth_available

    def collect_items(self, source_ref):
        return [{"id": "thread", "target": str(source_ref), "content": "Fake email thread text for snapshot only."}]


class FakeSlackThreadAdapter(ConnectorAdapter):
    name = "fake_slack_thread"
    source_types = ["slack_thread"]
    auth_required = True
    draft_allowed_actions = ["draft"]

    def __init__(self, provider=None, auth_available=False):
        super().__init__(provider=provider)
        self.auth_required = not auth_available

    def collect_items(self, source_ref):
        return [{"id": "thread", "target": str(source_ref), "content": "Fake channel thread text for snapshot only."}]


ADAPTERS = {
    "local_file": LocalFileAdapter,
    "local_repo": LocalRepoAdapter,
    "fake_url": FakeUrlSnapshotAdapter,
    "fake_drive_doc": FakeDriveDocAdapter,
    "fake_gmail_thread": FakeGmailThreadAdapter,
    "fake_slack_thread": FakeSlackThreadAdapter,
}


def make_adapter(name, provider_root=None, auth_available=False):
    provider = FakeProvider(provider_root) if provider_root else None
    cls = ADAPTERS[name]
    if name.startswith("fake_") and name not in {"fake_url"}:
        return cls(provider=provider, auth_available=auth_available)
    return cls(provider=provider)
