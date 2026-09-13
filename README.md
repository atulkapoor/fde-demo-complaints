# fde-demo-complaints

The second complete engagement through
[fde-framework](https://github.com/atulkapoor/fde-framework), on real data:
2,034 real consumer complaints from the public
[CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/),
each carrying the company's actual recorded outcome — the decision label.
Where [the first demo](https://github.com/atulkapoor/fde-demo-receipts)
proved the extraction shape, this one proves the *decision* shape: a system
that acts through external systems, with the agent posture the framework
decides rather than bolts on.

This is also the framework's **first fully green implement loop** —
holdout included.

## The run, in numbers

| Stage | Result |
|---|---|
| Data | 2,034 unique complaints with narratives, pulled from the public API across five products |
| The exam refused ambiguous truth | `fde samples` rejected the first pair file: two real complaints had byte-identical narratives and *different* recorded outcomes — *"a specification question for the client, not noise to average away."* 334 rows over 70 ambiguous narratives excluded before the exam existed |
| Gates | Passed on real evidence: a sqlite store that returned 2,034 real rows, a recorded baseline (operational figures a stated scenario, labelled as such; decision ground truth is the recorded `company_response`), security self-review on file, eval owner interviewed |
| Steering | The middle of the engagement was driven by `fde next` — every recording command names the next move, and the ladder handed over statement → interviews → gates → exam → build in order |
| Architecture | customer-vpc; **agent posture decided from the facts**: every outward call through one governed tool boundary, `approve-integration` and `critic-integration` in front of anything irreversible, an idempotency key so re-running cannot act twice. And the fashionable planner lost on the record: `model-planner — optimisation is simpler and applies here` |
| Implement | Round 1 red (7 files), **round 2 green**: golden 72.6%, adversarial 100%, **holdout 63.3%** — thirty complaints the delivery never shipped, tracking the golden score honestly. Majority-class floor for context: ~42% |

## What this run found

- The duplicate-label refusal above — on real data, first try. Identical
  text with different outcomes means text alone under-determines the
  decision; that is a finding about the client's process, surfaced before
  a single line of code.
- Both this engagement's statement and the first demo's parsed the word
  "Decide each…" to nothing — the shape came from the labelled pairs
  instead. Fixed upstream the same day (the phrase now reads as a
  decision workload).
- `fde next` initially trapped on a question nobody could honestly answer
  (the unmeasured rule-path coverage — the framework's own flagship case
  says building with that unknown *is* the answer). Fixed the same day:
  the ladder now asks only while an answer could change what gets built.

## Reproduce it

Nothing is redistributed here; everything regenerates from the public API.
The CFPB database grows daily, so a fresh pull yields fresh complaints —
the numbers above pin the run this repository records.

```bash
python3 prepare.py    # fetches from the public API, builds pairs/holdout/store

python3.12 -m venv venv && venv/bin/pip install "fde-framework>=0.1.8"
venv/bin/fde start complaints --statement "Decide each incoming consumer complaint: monetary relief, non-monetary relief, or close with an explanation; the decision reaches the CRM, billing, and the letters system."
venv/bin/fde samples complaints --file engagement-prep/pairs.jsonl
cp engagement-prep/holdout.jsonl engagements/complaints/artifacts/holdout.jsonl
venv/bin/fde next complaints     # and keep doing what it says
# ... interviews, baseline, data-access, security-review, per the ladder
venv/bin/fde build complaints --out project
venv/bin/fde implement project --holdout engagements/complaints/artifacts/holdout.jsonl \
  --max-rounds 6 --check "python evals/harness.py --min-score 0.6"
```

**The deliverable itself is committed under [`project/`](project/)** — the
emitted project at its green state: the decision pipeline, the governed
tool boundary with approval gates, critics and the idempotency key,
deploy assets, runbook and diagnosis walk. Only the case files
regenerate (they embed complaint text).

The recorded interviews, baseline, and implement round log are in this
repository (`engagements/`, `implement-run.log`).

## Transcripts, verbatim

The exam refusing ambiguous ground truth, before any code existed:

```
complaint-041 and complaint-061 have the same input and disagree on ['decision'].
That is a specification question for the client, not noise to average away.
```

The helping hand steering the middle of the engagement — every recording
command ends by naming the move:

```
data access recorded
next: fde baseline complaints --file baseline.yaml
baseline recorded -- re-measurable, sampled, complete
next: fde security-review complaints --note "who looked, at what"
```

And the framework's first fully green loop, holdout included, as the
round log wrote it:

```
## Round 2

- check: green

metrics: field_exact_match, field_coverage
  golden         84 cases  72.6%
  adversarial     2 cases  100.0%
holdout: green (cases the implementer never saw)

**Stopped by**: harness green.
```

## Honesty notes

- The 0.6 bar is deliberate: three-way decisions from redacted narrative
  text are harder than field extraction, the majority class sits at ~42%,
  and the holdout still guards the gap. The receipts demo used 0.85 for
  the easier shape.
- Operational baseline figures are a stated scenario, labelled as such in
  the recorded baseline. The decision ground truth is real: the outcome
  the company actually recorded for each complaint.
- CFPB narratives are published with PII redacted at source (the XXXX
  blocks). This repository stores none of them; `prepare.py` pulls from
  the public API.
- One engagement on public data still is not a production engagement:
  the framework's status remains **built, demonstrated, unproven**.
