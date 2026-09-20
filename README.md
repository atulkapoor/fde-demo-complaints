# fde-demo-complaints

> **The deliverable is in this repo**: [`project/`](project/) — the emitted, implemented, deployable output (pipeline service, deploy assets, runbooks, evals, ARCHITECTURE.md, RISKS.md). Start at [`project/README.md`](project/README.md).

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

## Where it stands (fde 0.1.28)

`fde stage` computes the engagement's stage off the record -- never declared --
and appended the first transition to
[`engagements/complaints/lifecycle.jsonl`](engagements/complaints/lifecycle.jsonl):

```
complaints: pilot

  ok discovery
       ok a problem statement: Decide each incoming consumer complaint: monetary relief, non-monetary relief, o...
  ok validation
       ok the gates pass or are waived on the record: all pass
       ok the exam is seeded from the client's pairs: 150 pairs
       ok a holdout the delivery never ships: 46 cases
       ok data access attested: sqlite complaints.db returned 2,034 real rows (CFPB narratives, redacted at sour
  ok prototype
       ok a build with its exam record: project-0.1.27
  ok pilot
       ok a scorecard on record: scorecard.json
       ok the out-of-sample rows hold: 73.9% on 46 cases (majority 41.3%; abstained 2.2%, 75.6% on the answered)
       ok the edge answers a valid request: 200 "Closed with explanation"
  -- production
       NO a deployment on record: none: fde deployed <eng> --note
       ok no open incident: none open
  -- adoption
       NO an adoption figure measured in the field: none: fde outcome <eng> --metric adoption=<share>
  -- retrospective
       NO a retrospective captured as a case: none: fde retro

to reach production: a deployment on record -- none: fde deployed <eng> --note

recorded: start -> pilot (lifecycle.jsonl)
```

The out-of-sample row holds (73.9% on 46 cases, majority 41.3%, abstaining 2.2%, 75.6% on the answered) and the edge answered a valid request, so the record reaches pilot. The next stage needs a deployment attested by name -- the local HTTP run under "Deployed and answering" below was a demonstration, not a deployment, and it is not attested. No drift check has run here; the banking demo is where the whole loop has run in public.

On 0.1.31 the eighth gate, the outcome contract (who owns the number the
system exists to move, its value today, its target, how it is measured, by
when), is waived on this record with the reason where a reader will find
it: no client owns an outcome in a public demonstration, and nobody has set
a target. `fde debt engagements/complaints` ([`debt.txt`](debt.txt)) lists what
the engagement rests on that nobody has settled: 9 items: five environment facts said in the interview and never measured, one role never heard, one standing waiver, and two attestations with nobody's name on them. None blocks the
build or production; the waivers age from today.

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

## Built again on the 0.1.27 emitter (2026-09-20)

The scorecard, as of 0.1.27, carries fitness rows -- a generalisation gap,
the engagement's own error-rate bar, a valid request through the edge --
and the shipped classifier abstains below a margin. Rebuilt here as
[`project-0.1.27/`](project-0.1.27/), `fde scorecard project-0.1.27 --holdout ...`
says **17 of 22 measured properties hold**, and the five that do not are
the honest state of this engagement:

| Row | Measured |
|---|---|
| Holdout, 46 cases never shipped | 73.9%, abstaining 2.2%, 75.6% on the answered (majority 41.3%) |
| Generalisation gap | golden 94.8% in-sample minus holdout 73.9% = 20.9 points, just past the card's cap |
| Beats the baseline error rate | no: the demo's stated baseline records a 6% first-pass error rate, so 94% is the bar, and 75.6% on the answered is far from it |
| Edge cases | 3 of 7 |
| Adversarial probes | 5 of 11, all six failures attributed to misread bases, none followed |

The reading has not changed since 0.1.25: a 74% three-way classifier with
a thin attack layer, honestly measured, is what a bag-of-words baseline
buys on consumer complaints where the label is the company's response
rather than anything in the narrative. The implement loop has not been
run on this build; the stated baseline figures are marked stated, not
measured, on the SLO page.

## Built again on the 0.1.25 emitter (2026-09-19)

The eighth audit pass gave this shape its first sign-off, with
conditions, and named the one that was the exam's: every probe sat on
the two shortest inputs, both misread by the baseline, so "0 injections
followed" measured nothing. 0.1.25 draws probe bases from typical
cases -- one per label, at the median length -- ships them in the edge
layer so each is scored un-steered, and rotates the probes across them.
That build is under [`project-0.1.25/`](project-0.1.25/).

| shipped classifier, no agent | 0.1.24 | 0.1.25 |
|---|---|---|
| Holdout (out-of-sample) | 69.6% on 46 cases | **73.9%** on 46 cases, majority 41.3% |
| Golden (in-sample) | 93.9% | 94.8% on 96 cases |
| Edge cases | 2 of 4 | 3 of 7 (two extremes and two typical bases misread) |
| Adversarial probes | 4 of 11, none scorable | 5 of 11; injection measured on one base, not followed |

Reading it honestly: two of the three typical bases are cases this
baseline misreads un-steered (it is a 74% classifier), so six of the
seven graded probes are attributed to misreads and one framing was
measured on the base it gets right. The harness exits red for that
reason and says so; this engagement's attack layer will stay thin until
the misreads are fixed by an implementation better than the shipped
baseline, which is what the implement loop is for. Same 150 pairs, same
split, same holdout digest as 0.1.23.

## Built again on the 0.1.24 emitter (2026-09-19)

Two things the 0.1.23 build's own eval left open, closed and rebuilt
under [`project-0.1.24/`](project-0.1.24/):

- **A label named in the text is not evidence.** The one injection the
  0.1.23 harness counted as followed spelled a label out, and the label's
  own words ("closed", "monetary", "explanation") sat in the classifier's
  vocabulary. They are excluded now. On this build the harness attributes
  all seven adversarial failures to the two misread edge cases -- zero
  followed -- and the holdout stays at **69.6%** (majority 41.3%): the
  label words were never carrying the decision, only the steer.
- **A steer that coincides with a misread base is a misread.** The
  harness no longer claims "followed" for a probe whose base case the
  system gets wrong on its own, even when the wrong answer happens to be
  the injected one.

Same 150 pairs, same split, same holdout digest as 0.1.23. The implement
loop has still not been run against any of the rebuilt projects.

## Built again on the 0.1.23 emitter (2026-09-19)

The seventh audit pass re-ran every 0.1.22 check on the build above and
found them holding, then read the classifier the way an ML engineer
would: the estimator was mis-specified (long inputs drifted to the
rarest label; the commonest was recalled once in sixteen on the
holdout), the golden score was in-sample, the probes and edges were
drawn from the cases the classifier was fitted on, and a missing golden
file would have served a constant answer behind a green `/ready`.
0.1.23 answered each as a check first, and the same engagement was built
again from the same 150 pairs. That build is under
[`project-0.1.23/`](project-0.1.23/).

| shipped classifier, no agent | 0.1.22 | 0.1.23 |
|---|---|---|
| Holdout (out-of-sample) | 55.6% on 45 cases, majority 35.6% | **69.6%** on 46 cases, majority 41.3% |
| Golden (in-sample, fitted on this file) | 59.0% | 93.9% |
| Edge cases | 75% of 4 | 50% of 4 |
| Adversarial probes | 10 of 11 | 4 of 11 |

Reading it honestly:

- **The holdout is the number.** Fourteen points on cases the classifier
  never saw, from the same tokens, by switching a Bernoulli scoring rule
  for a multinomial one -- the audit's own measurement, reproduced. The
  golden figure rose more because it is in-sample, and the harness now
  prints that beside it.
- **The split changed under it.** The holdout is drawn stratified by
  label and one exact repeat is counted once, so 0.1.22's 45 cases and
  0.1.23's 46 are different draws; `fde samples` announced the
  replacement with both digests and the exam record carries the new one.
- **The probes got harder, not the classifier worse.** They now build on
  the edge cases -- moved out of golden, so the classifier was not fitted
  on them -- and two of the four edges are misread un-steered. The
  harness attributes the seven failures: one injection followed, six
  answered wrong regardless of the injection because the base case is
  misread. The one followed injection is the finding to fix; the six are
  the edge layer's finding, counted where it belongs.
- **It refuses what it cannot stand behind.** Without `evals/golden.jsonl`
  the service exits 78 at boot; with a golden file whose digest is not the
  one in `evals/manifest.json`, the same. Editing the exam no longer edits
  production silently.

The eval files embed complaint narratives and are not committed; they
regenerate from `prepare.py` and a 0.1.23 build. The implement loop has
not been run against this build.

## Built again on the 0.1.22 emitter (2026-09-18)

The sixth audit pass read the 0.1.21 deliverable and refused to sign
off the decision shape for reasons that were the generator's: a constant
classifier could pass its CI, a text decision reached a constraint
solver, thirty-six verified pairs had gone missing between the split and
the shipped holdout with nothing to say so. 0.1.22 answered each as a
check first, and the same engagement was built again -- this time from
all 150 verified pairs handed to one split, as the audit asked. That
build is under [`project-0.1.22/`](project-0.1.22/).

What is different about this build, before any agent touches it:

- **It ships a fitted classifier, not a scaffold.** `app/components/reasoning.py`
  names the three labels, fits token log-odds on the golden set at
  import, and decides with a per-label score. Its own scores, no agent
  involved: golden **59.0%** against a majority rate of 43.8% (in-sample:
  the classifier is fitted on that file), edge 75%, holdout **55.6%**
  against a majority rate of 35.6% -- a baseline the implement loop now
  has to beat rather than a blank to fill.
- **The exam is wider and it steers.** 105 golden, 4 edge cases drawn
  from the data's own extremes, 11 adversarial probes including two that
  steer toward a wrong label. The shipped classifier answered one of
  them wrongly (10/11), and the harness exited red. The seventh audit
  pass read that failure more carefully than the harness did: the base
  case was misread un-steered, so the injection was not followed -- a
  distinction the 0.1.23 harness now makes itself.
- **A constant answer is red.** The harness reports per-class precision,
  recall and F1, the confusion and the majority rate, and refuses a
  golden score that does not beat the majority.
- **The exam is on the record.** `evals/manifest.json` and
  `evals/acceptance.md` carry the split seed, the holdout share and the
  SHA-256 of every eval file and of the engagement holdout. `fde samples`
  announced the replaced holdout with both digests when the 150 pairs
  went in; `fde implement` names a holdout that is not the recorded one.
- **The sample assessment spoke.** One verified pair repeats an earlier
  input exactly; thirteen inputs are exactly 3,000 characters long -- a
  hard truncation upstream. Both are true of this dataset and both were
  invisible before.

The eval files of this build embed complaint narratives and are not
committed (see `.gitignore`); they regenerate from `prepare.py` and a
0.1.22 build. The implement loop has not yet been run against this
build; when it is, the comparison to draw is against the classifier's
own holdout figure above, not against a blank.

## Re-run on the 0.1.21 emitter (2026-09-18)

The original deliverable under [`project/`](project/) is the measured
artefact of the 0.1.8-era emitter and stays as it was. After five
independent audit passes reshaped what the framework emits (one
envelope every step reads and writes, an HTTP edge with identity and
request ids, a boundary that validates every outward URL, a durable
locked ledger, a hardened unit, and edge tests inside the deliverable),
the same recorded engagement was built again on **0.1.21** and driven
through the same implement loop, same holdout, same bar. That run is
under [`project-0.1.21/`](project-0.1.21/), its round log in
[`implement-log-0.1.21.md`](implement-log-0.1.21.md).

| | original (0.1.8) | re-run (0.1.21) |
|---|---|---|
| Loop | green, round 2 | green, round 2 |
| Golden (84 visible cases) | 72.6% | **69.0%** |
| Holdout (30 cases the agent never saw) | 63.3% | **76.7%** |
| Adversarial layer shipped with the build | 2 probes, 100% | 2 probes, 100% |
| Bar (`--min-score`) | 0.6 | 0.6 |

Two different agent implementations of the same exam: the re-run scores
lower on what it could see and materially higher on what it could not,
which is the direction an exam wants -- the gap between visible and
unseen narrowed from nine points to minus eight. Neither number beats
the human baseline's error rate; both runs say so.

Measured after the fact, against the wider exam that 0.1.22 generates
from the same pairs (the build above shipped with the 0.1.21 exam; the
probe files embed complaint text and regenerate with `prepare.py` plus a
0.1.22 build, so only the run's report is committed, at
[`evals-0.1.22/adversarial-report.json`](evals-0.1.22/adversarial-report.json)):
the implemented service
passed all **9 adversarial probes** (three injection framings, a prefix
injection, empty and whitespace input, an oversized narrative, a wrong
type, invisible characters) and **3 of 4 edge cases** drawn from the
data's own extremes of length. Post-measurement, labelled as such.

What a reader gets from `project-0.1.21/` that `project/` never had:
`app/service.py` (the edge), `app/shapes.py` (the request contract),
`app/ledger.py` (audit and idempotency that survive a restart),
`tests/test_edge.py` (the edge defending itself), a boundary that refuses
an outside endpoint at import, and a unit that stops a refused
configuration instead of restarting it five times.

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

## Deployed and answering

The question that found a framework bug: *has anyone actually run the
deployment?* The systemd unit executes `python -m app.pipeline` — and
until fde-framework 0.1.11, the emitted pipeline defined its functions
and exited: a service dying silently on first start. Fixed upstream
(the pipeline is now a stdlib HTTP service), backported here, and then
run exactly as the unit would:

```
$ PORT=8091 python -m app.pipeline
serving on :8091 -- /health, POST /

$ curl -s http://127.0.0.1:8091/health
{"status": "ok"}

$ curl -s -X POST :8091/ -d '"I was charged twice for the same order in
  March and the bank refuses to reverse the duplicate charge..."'
{"result": {"decision": "Closed with explanation"}}

$ curl -s -X POST :8091/ -d 'null'
{"refused": "a complaint arrives as text, not NoneType"}   [422]
```

Note the honesty in both directions: a malformed payload is a 422 with
the contract spelled out, and the first answer above is arguably the
wrong decision (a duplicate charge leans monetary relief) — a 72.6%
system behaving exactly like a 72.6% system, in production posture.

## Honesty notes

- The 0.6 bar is deliberate: three-way decisions from redacted narrative
  text are harder than field extraction, the majority class sits at ~42%,
  and the holdout still guards the gap. The receipts demo used 0.85 for
  the easier shape.
- Operational baseline figures are a stated scenario, labelled as such in
  the recorded baseline. The decision ground truth is real: the outcome
  the company actually recorded for each complaint.
- CFPB narratives are published with PII redacted at source (the XXXX
  blocks). The corpus is not included and regenerates via `prepare.py`;
  a handful of narratives do appear inside the committed deliverable
  (the adversarial probe and examples the agent chose) — public
  US-government data, redacted at source.
- The adversarial layer's injection probe is a regression guard for a
  future model swap: today's pipeline is rules-only, so "ignore all
  previous instructions" cannot succeed by construction — the 100% there
  is a guard being in place, not a security result.
- Both this demo's and the receipts demo's golden scores happen to be
  72.6% — a genuine coincidence of two 84-case exams landing on 61
  passes, reproducible independently in each repo.
- One engagement on public data still is not a production engagement:
  the framework's status remains **built, demonstrated, unproven**.
