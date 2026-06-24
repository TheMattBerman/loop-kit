# tests/test_loop_index.py
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
def test_index_schema_and_no_bodies():
    data = json.loads((ROOT / "shared/library/loop-index.json").read_text())
    assert isinstance(data, list) and len(data) >= 12
    required = {"id","slug","title","source","url","tags","archetype","maturity","why_fits"}
    sources = set()
    for e in data:
        assert required.issubset(e.keys()), f"missing keys in {e.get('slug')}"
        assert "prompt" not in e and "body" not in e and "verification" not in e, "prompt bodies must not ship"
        assert e["maturity"] in {"L0","L1","L2","L3","L4"}
        sources.add(e["source"])
    assert len(sources) >= 3, "library must be multi-source"
