# Risks accepted

No gate was waived and no recommendation overridden. Every component in scope was decided; decided is not implemented -- see below for what still raises.

## Decided, not yet implemented

These modules carry their contract and raise on use until the implementation step (by hand, or `fde implement`) fills them. A green evaluation is impossible while any is on the payload path.

- `reasoning`

## Identity at the edge

One bearer token, one service principal, one set of scopes: every caller acts as the same identity, so the audit names the service, not a person. Per-caller identity is an `access_model` decision nobody has answered; accept this or front the service with something that does.

## Unanswered assumptions

Decisions were made without these facts. Each is a risk until somebody answers it (`fde ask`, or the interview), and the answer may change a decision.

- cheap_path_coverage: not stated, so nothing was decided on it
- confidence_calibrated: not stated, so nothing was decided on it
- latency_budget_ms: not stated, so nothing was decided on it
- sensitivity_present: not stated, so nothing was decided on it

