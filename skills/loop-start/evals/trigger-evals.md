# loop-start Trigger Evals

loop-start fires when a non-technical person describes a goal in everyday words and
wants AI to handle it for them. It is the plain-language front door.

It does NOT fire when the user already speaks in design terms and wants to spec or map
a loop (route that to loop-builder), and it does NOT fire when the user wants to audit,
critique, or triage an existing loop (route that to loop-doctor).

## 3-Way Routing

| Skill | Fires on |
|---|---|
| loop-start | beginner / plain-language intent ("I want AI to do X for me") |
| loop-builder | design / spec / map intent ("design a loop for X") |
| loop-doctor | audit / critique / triage intent ("is this loop safe?") |

No phrasing below appears in the Should Fire list of loop-builder or loop-doctor.
Their design phrasings and audit phrasings are listed here only as Should NOT Fire.

## Should Fire

These plain-language phrasings route to loop-start:

- "I want AI to do my X for me"
- "help me automate X"
- "get AI to handle X every day"
- "set up AI to do X for me"
- "can AI do X so I do not have to?"
- "I do not know what a loop is but I want Y to happen on its own"
- "make AI take care of X without me"
- "I want something to run X for me every morning"
- "how do I get AI to just handle this for me?"
- "I am not technical, can you set this up so AI does X?"

## Should NOT Fire

### Belongs to loop-builder (design / spec / map)

- "design a loop for X"
- "build me a goal routine"
- "turn this workflow into a loop"
- "help me spec a recurring automation"
- "create a scheduled agent"
- "map this repeating job"
- "what would this look like as a loop?"
- "spec out an automation from scratch"

### Belongs to loop-doctor (audit / critique / triage)

- "audit this loop spec"
- "critique this automation"
- "should I automate this?"
- "is this loop safe to run?"
- "why is my loop producing junk?"
- "review my recurring agent workflow"
- "is this a good loop?"
- "triage this agent loop"

## Disjointness Check

Cross-checked against `skills/loop-builder/evals/trigger-evals.md` and
`skills/loop-doctor/evals/trigger-evals.md`: every loop-start Should Fire phrasing is
absent from both siblings' Should Fire lists, so no single phrasing fires two skills.
The design phrasings and audit phrasings appear above only as Should NOT Fire, matching
each sibling's own Should Fire set.
