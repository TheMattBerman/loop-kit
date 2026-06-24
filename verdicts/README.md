# Verdicts Log

This directory captures operator corrections to loop-kit judgments. When a human overrides
a verdict produced by `loop_onboard.py` or `design_judge.py`, append a JSONL line to
`verdicts/log.jsonl` using the schema below. These lines serve as few-shot examples: feed
them back into future prompts or fine-tuning runs so the kit improves over time.

`example.jsonl` is the illustrative sample committed with the kit; the live correction log is `verdicts/log.jsonl`, which is created on first append and may be gitignored or committed per the operator's choice.

## Schema

Each line is a JSON object with three required fields:

```
{
  "situation": "<the original input or spec that produced the wrong verdict>",
  "judgment": "<the verdict the kit produced>",
  "fix":      "<what the correct verdict or guidance should have been and why>"
}
```

## How to use

1. Run a loop through `loop_onboard.py` or `design_judge.py`.
2. If the operator decides the output is wrong, add one line to `verdicts/log.jsonl`.
3. Before the next significant prompt session, load the recent lines as few-shot examples
   in the system prompt so the LLM can learn from past corrections.
4. Run `scripts/compare-baseline.sh` after every batch of corrections to confirm the
   golden cases still pass (the kit has not regressed on known-good examples).

## Full LLM A/B (manual step)

Comparing the kit against a vanilla LLM baseline is a documented manual step:
1. Run the same set of inputs through `loop_onboard.py` (kit) and a raw LLM prompt (baseline).
2. Score both sets against your verdict criteria.
3. If the kit loses ground, review recent changes and verdict corrections for regressions.
The automated `compare-baseline.sh` gate covers golden-case regression only; the full A/B
requires human evaluation.
