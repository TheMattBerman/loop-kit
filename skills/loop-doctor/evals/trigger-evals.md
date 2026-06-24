# loop-doctor Trigger Evals

loop-doctor fires when the user wants to audit, critique, or triage an existing loop.
It does NOT fire when the user wants to design or build a new loop from scratch (route that to loop-builder).

## Should Fire

These phrasings route to loop-doctor:

- "audit this loop spec"
- "critique this automation"
- "should I automate this?"
- "is this loop safe to run?"
- "why is my loop producing junk?"
- "review my recurring agent workflow"
- "is this a good loop?"
- "triage this agent loop"
- "check if my loop is ready to schedule"
- "what's wrong with my existing loop?"

## Should NOT Fire

These phrasings do NOT route to loop-doctor (route to loop-builder instead):

- "design a loop for X"
- "build me a goal routine"
- "turn this workflow into a loop"
- "help me spec a recurring automation"
- "create a scheduled agent"
- "map this repeating job"
- "what would this look like as a loop?"
- "I have a rough idea, help me build a loop"
- "spec out an automation from scratch"
