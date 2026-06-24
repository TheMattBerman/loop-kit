import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from evidence_packets import append_evidence, make_evidence, read_evidence, validate_evidence
from source_snapshots import build_snapshot


def test_evidence_record_has_required_contract_fields(tmp_path):
    snapshot = build_snapshot("local_file", "source.txt", "local_file", [{"id": "1", "content": "ok"}])
    evidence = make_evidence(snapshot, "source.txt")
    validation = validate_evidence(evidence)
    assert validation["valid"]
    assert evidence["snapshot_id"] == snapshot["snapshot_id"]
    append_evidence(evidence, tmp_path)
    loaded = read_evidence(tmp_path / "evidence.jsonl")
    assert loaded[0]["evidence_id"] == evidence["evidence_id"]
