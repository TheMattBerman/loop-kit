import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "scripts"))

import plain_language


JARGON = re.compile(r"\bR[0-4]\b|\bL[0-4]\b|archetype|downgrade-to-prompt|not-a-loop|fix-then-go|verdict|maturity|risk", re.I)
ALLOWED_QUESTION_STARTS = (
    "What should I inspect",
    "What would make one run count as finished",
    "Which actions must I ask you to approve",
    "Which decisions need your approval",
    "What should I hand back",
)


def test_six_beginner_golden_prompts_are_plain_and_blocker_only():
    cases = json.loads((ROOT / "golden" / "beginner_cases.json").read_text())
    assert len(cases) >= 6
    for case in cases:
        packet = plain_language.beginner_packet(case["input"])
        blob = json.dumps(packet)
        assert not JARGON.search(blob), case["id"]
        assert len(packet["questions"]) <= 3, case["id"]
        for question in packet["questions"]:
            assert question.startswith(ALLOWED_QUESTION_STARTS), (case["id"], question)
        assert "I will run the first version safely, with checkpoints." in packet["first_run"]
        assert "create the first-run checkpoint" in packet["on_my_own"], case["id"]
        assert "capture evidence" in packet["on_my_own"], case["id"]
        assert any("sends, posts, publishes" in item for item in packet["checks_with_you_first"]), case["id"]
        assert "freeze the source before acting" in packet["first_run_instructions"], case["id"]
        assert "write evidence and verifier results before closing the run" in packet["first_run_instructions"], case["id"]
        assert packet["runnable_command"].startswith("python3 shared/scripts/checkpoint_run.py init"), case["id"]
        assert "what evidence I captured" in packet["output_packet"], case["id"]
        assert "whether this should run again" in packet["output_packet"], case["id"]
