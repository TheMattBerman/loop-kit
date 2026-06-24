"""Fake connector providers with side-effect ledgers for V3-A tests."""

import json
from pathlib import Path


FORBIDDEN_LEDGERS = ["writes.jsonl", "deletes.jsonl", "sends.jsonl", "merges.jsonl", "deploys.jsonl"]


class FakeProvider:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _append(self, name, payload):
        path = self.root / name
        with path.open("a") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
        return str(path)

    def read(self, adapter, source_ref, items):
        return self._append("reads.jsonl", {"adapter": adapter, "source_ref": str(source_ref), "item_count": len(items)})

    def draft(self, adapter, target, payload_hash):
        return self._append("drafts.jsonl", {"adapter": adapter, "target": str(target), "payload_hash": payload_hash})

    def forbidden_side_effects(self):
        entries = {}
        for name in FORBIDDEN_LEDGERS:
            path = self.root / name
            if path.exists() and path.read_text().strip():
                entries[name] = path.read_text().splitlines()
        return entries
