# tests/test_plain_language.py
import re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "shared" / "scripts"))
import plain_language as pl

JARGON = re.compile(r"\bR[0-4]\b|\bL[0-4]\b|archetype|downgrade-to-prompt|not-a-loop|fix-then-go", re.I)

def test_mappers_return_plain_nonempty_strings():
    assert "check" in pl.plain_archetype("Verification Loop").lower()
    assert pl.plain_risk("R2 artifact changes")
    assert pl.plain_maturity("L1 manual loop")
    for v in ["go", "fix-then-go", "downgrade-to-prompt", "not-a-loop"]:
        assert pl.plain_verdict(v)
    assert pl.plain_danger("unsafe_external_action")

def test_unknown_inputs_fall_back_not_raise():
    for f in (pl.plain_archetype, pl.plain_risk, pl.plain_maturity, pl.plain_verdict, pl.plain_danger):
        out = f("something-unmapped-xyz")
        assert isinstance(out, str) and out.strip()

def test_no_mapper_output_contains_jargon():
    samples = [
        pl.plain_archetype("Verification Loop"),
        pl.plain_risk("R4 external actions"),
        pl.plain_maturity("L3 scheduled loop"),
        pl.plain_verdict("downgrade-to-prompt"),
        pl.plain_danger("unsafe_external_action"),
    ]
    for s in samples:
        assert not JARGON.search(s), f"jargon leaked: {s}"

def test_plainify_shape():
    result = {"archetype": "Review Queue Loop", "risk": "R1 read-only review",
              "maturity": "L1 manual loop", "flags": ["unsafe_external_action"]}
    out = pl.plainify(result)
    assert set(out.keys()) == {"what_it_does", "careful_because", "how_it_starts", "watch_for"}
    assert isinstance(out["watch_for"], list) and out["watch_for"]
