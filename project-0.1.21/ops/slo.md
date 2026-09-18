# Service objectives

Two buckets, because reporting one is half a story. A technical number nobody outside the team cares about, and a business number nobody inside it can move directly -- and a system healthy on the first while the second does not move is a system nobody will renew.

## Technical

- **Latency** — p95 under <not stated>ms at expected peak. Measured at the edge, not inside a component, because that is where somebody experiences it.
- **Availability** — business hours: planned windows outside them are free.
- **Evaluation score** — the golden layer at or above the threshold CI gates on. A drop here is a regression whether or not anything is down.
- **Adversarial score** — tracked separately and never averaged in. Scoring well on golden and badly on adversarial means nobody has attacked it yet.

## Business

- **The thing that should move** — stated by whoever asked for this, in their words, before it was built. If nobody can say what should change, that is the finding.

## Baseline

**Captured.** The numbers to beat, by their recorded definitions:

- **volume** — 2600 complaints/month (complaints entering triage (demo scenario figure, labelled simulated in the demo README))
- **cycle_time_per_unit_seconds** — 420 s (complaint opened to decision recorded, by hand (scenario))
- **labour_hours_per_week** — 60 h/week (triage team reading and deciding (scenario))
- **rework_rate** — 0.09 ratio (decisions reversed on callback (scenario))
- **exception_rate** — 0.14 ratio (escalated past triage (scenario))
- **error_rate** — 0.06 ratio (decision disagreeing with the labelled outcome (scenario))
- **business_metric** — 26 hours (mean complaint age at decision (scenario))
- sampled: n=40, demo engagement on the public CFPB corpus; operational figures are a stated scenario, decision ground truth is the recorded company_response

Re-measure by identical definitions in 60 days. A comparison that quietly changes a definition is a comparison with its thumb on the scale.
