# tests/test_loop_onboard.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "shared" / "scripts"))
import loop_onboard

def test_bad_loop_flags_and_refuses():
    out = loop_onboard.map_loop("set up an agent that keeps improving and publishing my posts until they are good")
    assert "vague_done" in out["flags"]
    assert "unsafe_external_action" in out["flags"]
    assert "Do not build as written" in out["recommendation"]

def test_out_of_vocab_does_not_crash():
    out = loop_onboard.map_loop("keep my newsletter ideas fresh")
    assert isinstance(out, dict)
    assert "recommendation" in out
