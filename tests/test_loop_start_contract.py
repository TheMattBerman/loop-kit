# tests/test_loop_start_contract.py
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "scripts"))
import loop_onboard, plain_language as pl

JARGON = re.compile(r"\bR[0-4]\b|\bL[0-4]\b|archetype|downgrade-to-prompt|not-a-loop|fix-then-go|Loop\b", re.I)

INPUTS = [
    "have AI check my competitors prices every morning and tell me what changed",
    "review my blog drafts before they publish",
    "publish my posts automatically until they look good",
    "summarize my unread emails every afternoon",
]

def test_plainify_over_real_map_loop_is_jargon_free():
    for q in INPUTS:
        plain = pl.plainify(loop_onboard.map_loop(q))
        blob = " ".join([plain["what_it_does"], plain["careful_because"],
                         plain["how_it_starts"], " ".join(plain["watch_for"])])
        assert blob.strip(), f"empty plain output for: {q}"
        assert not JARGON.search(blob), f"jargon leaked for {q!r}: {blob}"
