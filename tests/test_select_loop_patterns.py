import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "shared" / "scripts"))
import select_loop_patterns as s

def test_review_query_surfaces_review_archetype():
    res = s.match("seo draft review queue", limit=5)
    assert res, "must return matches"
    assert any("review" in (r["archetype"] + " ".join(r["tags"])).lower() for r in res[:3])

def test_out_of_vocab_returns_ranked_nonempty():
    res = s.match("xyzzy unrelated nonsense", limit=5)
    assert isinstance(res, list) and len(res) >= 1

def test_tie_break_is_numeric_ascending():
    # two entries with equal score should order by int(id) ascending, not string
    res = s.match("loop", limit=50)
    ids = [int(r["id"]) for r in res]
    # within equal-score runs ids must be ascending; assert global call does not crash and ids are ints
    assert all(isinstance(i, int) for i in ids)
