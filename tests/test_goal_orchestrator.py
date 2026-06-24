import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "library"))

from goal_orchestrator import build_goal_cycle, write_cycle_artifacts


def test_goal_cycle_passes_when_all_criteria_have_evidence():
    objective = "Build an agentic operating loop that creates worker packets and reviewer packets."
    criteria = ["agentic operating loop creates worker packets", "agentic operating loop creates reviewer packets"]
    report = "## Result\npass\n## Evidence\nagentic operating loop creates worker packets. agentic operating loop creates reviewer packets."
    cycle = build_goal_cycle(objective, result_report_text=report, success_criteria=criteria)
    assert cycle["decision"]["complete"]
    assert cycle["decision"]["verdict"] == "pass"


def test_goal_cycle_preserves_original_objective_on_partial():
    objective = "Build the full planner worker evaluator next-goal shuttle."
    cycle = build_goal_cycle(objective, result_report_text="## Result\npartial\n## Evidence\nplanner prompt exists.")
    assert cycle["decision"]["verdict"] == "needs_fix"
    assert objective in cycle["worker_kickoff_prompt"]
    assert objective in cycle["reviewer_prompt"]
    assert objective in cycle["next_goal_prompt"]


def test_goal_cycle_refuses_narrow_drift_completion():
    objective = "Turn Loop Kit into an agentic operating loop that plans work, reviews evidence, and writes next goals."
    report = "## Result\npass\n## Evidence\nrelease notes were updated."
    cycle = build_goal_cycle(objective, result_report_text=report)
    assert not cycle["decision"]["complete"]
    assert "original objective not fully evidenced" in cycle["decision"]["failures"]


def test_scheduler_and_connector_are_user_owned():
    scheduler = build_goal_cycle(
        "Help the user schedule a proven loop without installing cron.",
        result_report_text="## Result\npartial\n## Evidence\nschedule checklist exists.",
    )
    connector = build_goal_cycle(
        "Help the user connect Gmail evidence without authorizing the connector.",
        result_report_text="## Result\npartial\n## Evidence\nread-only evidence checklist exists.",
    )
    assert "User-owned scheduler setup" in scheduler["next_goal_prompt"]
    assert "User-owned connector setup" in connector["next_goal_prompt"]
    assert "installed scheduler" not in scheduler["next_goal_prompt"].lower()
    assert "authorized gmail" not in connector["next_goal_prompt"].lower()


def test_goal_cycle_writes_required_artifacts(tmp_path):
    cycle = build_goal_cycle("Build goal artifacts.", result_report_text="## Result\npartial\n## Evidence\nnone.")
    files = write_cycle_artifacts(cycle, tmp_path)
    assert set(files) == {
        "original-objective.md",
        "success-criteria.json",
        "worker-kickoff.md",
        "reviewer-prompt.md",
        "result-report.json",
        "evidence-checklist.json",
        "decision.json",
        "next-goal-prompt.md",
    }
    assert (tmp_path / "original-objective.md").exists()


def test_goal_orchestrator_cli_writes_artifacts(tmp_path):
    payload = {
        "objective": "Build a worker reviewer cycle.",
        "result_report": "## Result\npartial\n## Evidence\nworker exists.",
    }
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps(payload))
    output_dir = tmp_path / "cycle"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "shared" / "scripts" / "goal_orchestrator.py"), str(input_path), "--output-dir", str(output_dir)],
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert (output_dir / "decision.json").exists()
