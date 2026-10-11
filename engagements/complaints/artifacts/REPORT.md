# complaints: decision brief

Written by `fde report` on 2026-10-12 from the record at `engagements/complaints`. Every figure below is read off that record; nothing here is estimated. Where a section quotes a command, it is what the command prints today, and running it again is the way to check.

## The problem as stated

The first statement, as the client put it.

> Decide each incoming consumer complaint: monetary relief, non-monetary relief, or close with an explanation; the decision reaches the CRM, billing, and the letters system.

## Where the engagement stands

The stage is computed from the evidence on the record, not declared.

```text
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
       NO an adoption figure measured in the field: none: fde outcome <eng> --metric adoption=<value>
  -- retrospective
       NO a retrospective captured as a case: none: fde retro

to reach production: a deployment on record -- none: fde deployed <eng> --note
```

## What the record knows, and who said it

Every fact carries its source. A fact learned from a person or inferred is asserted, not established; the gates below say which ones still need establishing.

```text
known (23)
  functional scope:
    external_systems = 3   [Atul Kapoor, admin]
    input_format = text   [Atul Kapoor, eval_owner]
    output_shape = decision   [system]
    query_pattern = lookup   [Atul Kapoor, eval_owner]
    recall_span = within_turn   [Atul Kapoor, eval_owner]
  non-functional scope:
    access_model = single_operator   [Atul Kapoor, admin]
    availability_target = business_hours   [Atul Kapoor, admin]
    human_waiting = no   [Atul Kapoor, user]
    interpretability_required = False   [Atul Kapoor, eval_owner]
  data scope:
    arrival_rate = 90   [Atul Kapoor, eval_owner]
    corpus_churn = continuous   [Atul Kapoor, admin]
    corpus_size = 2034   [Atul Kapoor, eval_owner]
    data_residency = may_leave   [Atul Kapoor, admin]
    labelled_count = 120   [Atul Kapoor, admin]
  environment:
    accelerator = none   [Atul Kapoor, admin]
    container_competence = False   [Atul Kapoor, admin]
    environment_lifetime = permanent   [Atul Kapoor, admin]
    existing_cluster = False   [Atul Kapoor, admin]
    existing_iac_tool = none   [Atul Kapoor, admin]
    hosting = customer-vpc   [Atul Kapoor, admin]
    provisioning_api = False   [Atul Kapoor, admin]
  operations:
    operates_after_handover = app_team   [Atul Kapoor, admin]
  commercial:
    licence_posture = internal_only   [Atul Kapoor, sponsor]
  still open -- data scope: sensitivity_present · non-functional scope: cheap_path_coverage, confidence_calibrated, latency_budget_ms

87% of what gets decided is settled

waived (1)
  outcome_contract: no client owns an outcome: a public demonstration on CFPB complaint data; the baseline's business metric is stated, and nobody has set a target
```

## The number this system exists to move

No outcome contract is on the record; it is the eighth gate.

`fde outcome-contract` records the owner, the metric, its value today, the target, the method and the window -- or a waiver saying why not yet.

## The design, with its reasons

What `fde architect` decides from the facts above, with the approach each component takes and why; what could not be decided is listed under the risks. A build writes this same page as ARCHITECTURE.md.

Topology: **customer-vpc**  
Fingerprint: `0419def9054ec15a`

### Scope

**Functional scope**
- `external_systems` = 3
- `input_format` = text
- `output_shape` = decision
- `query_pattern` = lookup
- `recall_span` = within_turn

**Non-functional scope**
- `access_model` = single_operator
- `availability_target` = business_hours
- `human_waiting` = no
- `interpretability_required` = False

**Data scope**
- `arrival_rate` = 90
- `corpus_churn` = continuous
- `corpus_size` = 2034
- `data_residency` = may_leave
- `labelled_count` = 120

**Environment**
- `accelerator` = none
- `container_competence` = False
- `environment_lifetime` = permanent
- `existing_cluster` = False
- `existing_iac_tool` = none
- `hosting` = customer-vpc
- `provisioning_api` = False

**Operations**
- `operates_after_handover` = app_team

**Commercial**
- `licence_posture` = internal_only

### Decisions

| Component | Approach | Implemented with | Why |
|---|---|---|---|
| deployment | systemd-unit (advisory: decided and emitted, not a payload step) | plain-python | Service unit: always |
| evaluation | labelled-metrics (advisory: decided and emitted, not a payload step) | plain-python | Labelled metrics: output_shape == decision |
| governance | audit-only (advisory: decided and emitted, not a payload step) | plain-python | Audit trail: data_residency == may_leave |
| integration | governed-tools | plain-python | Governed tool boundary: external_systems > 1 |
| observability | traced (advisory: decided and emitted, not a payload step) | plain-python | Distributed tracing: always |
| perception | text-extraction | plain-python | Text extraction: input_format == text |
| planning | fixed-sequence | plain-python | Fixed sequence: always |
| provisioning | ansible-playbook (advisory: decided and emitted, not a payload step) | plain-python | Convergent configuration: provisioning_api == false |
| reasoning | labelled-decision | plain-python | Labelled decision from text: output_shape == decision and input_format == text |
| representation | deterministic | plain-python | Deterministic: output_shape == decision |

The tool boundary is emitted UNWIRED: no external system's tools are registered and the approval gate and critic are constructed without `approve=`/`review=`. Until the implementation registers tools and wires both, every action-shaped request is refused (409) -- fail closed, by design.

### Tools and libraries

| Component | Chosen | Licence | Alternatives in this topology |
|---|---|---|---|
| deployment | plain-python | PSF | -- |
| evaluation | plain-python | PSF | xgboost |
| governance | plain-python | PSF | -- |
| integration | plain-python | PSF | mcp |
| observability | plain-python | PSF | opentelemetry |
| perception | plain-python | PSF | -- |
| planning | plain-python | PSF | -- |
| provisioning | plain-python | PSF | -- |
| reasoning | plain-python | PSF | -- |
| representation | plain-python | PSF | -- |

Adopting an alternative the client already operates: `fde reuse <engagement> <stack>` and rebuild -- the architecture does not change, only the emitted code does.

### Agent and tool posture

- `integration` acts on the world. In front of it: approve-integration, critic-integration; an idempotency key derived from each action and reserved in the ledger (app/ledger.py) before it runs, so a retry cannot act twice.
- One operating team acts here; the audit names people, not roles.
- Tool boundary realized via `plain-python`.


### Rejected alternatives

What this design is not, and why. Usually the more useful half.

**deployment**
- `compose` -- ruled out by container_competence == false
- `kubernetes-manifests` -- ruled out by container_competence == false and existing_cluster == false

**evaluation**
- `field-match` -- nothing here matches output_shape == structured
- `judged` -- nothing here matches output_shape == freeform

**governance**
- `boundary-and-audit` -- ruled out by data_residency == may_leave
- `role-scoped-authority` -- ruled out by access_model == single_operator

**integration**
- `direct-call` -- ruled out by external_systems > 1

**observability**
- `structured-logs` -- ruled out by external_systems > 1

**perception**
- `ocr-pipeline` -- ruled out by input_format == text
- `passthrough` -- nothing here matches input_format == structured_data
- `speech-transcription` -- ruled out by input_format == text
- `video-ingestion` -- ruled out by input_format == text
- `windowed-ingestion` -- nothing here matches input_format == streams

**planning**
- `optimisation` -- ruled out by input_format == text
- `model-planner` -- fixed-sequence is simpler and applies here

**provisioning**
- `gitops` -- ruled out by existing_cluster == false
- `terraform-module` -- ruled out by provisioning_api == false
- `manual-runbook` -- ansible-playbook is simpler and applies here

**reasoning**
- `cascade` -- nothing here matches confidence_calibrated == true and cheap_path_coverage < 0.95 -- unanswered: cheap_path_coverage, confidence_calibrated (an answer could admit it)
- `classical-ml` -- ruled out by input_format == text
- `finetune` -- ruled out by output_shape == decision
- `llm` -- ruled out by output_shape == decision
- `optimisation-reasoning` -- ruled out by input_format == text

**representation**
- `assisted-deterministic` -- nothing here matches output_shape == structured and cheap_path_coverage < 0.95 and interpretability_required == true or output_shape == decision and cheap_path_coverage < 0.95 -- unanswered: cheap_path_coverage (an answer could admit it)
- `cascade` -- nothing here matches confidence_calibrated == true and cheap_path_coverage < 0.95 -- unanswered: cheap_path_coverage, confidence_calibrated (an answer could admit it)
- `classical-ml` -- ruled out by input_format == text
- `finetune` -- ruled out by output_shape == decision
- `llm-extraction` -- nothing here matches output_shape == structured
- `segmentation` -- nothing here matches output_shape == freeform

### Licences

Everything this design pulls in, so it can be checked before a legal team checks it.

- `plain-python`: PSF

## What the design rests on, and what was accepted

Waived gates, overridden recommendations, assumptions nobody has answered, and the facts the governance follows from. A build writes this same page as RISKS.md.

### Decided, emitted, not on the payload path

These components were decided and their modules are emitted, but the request path does not run them: the edge's structured log is the observability that runs, the ledger is the audit that runs, the unit is the deployment. Each module says so in its first lines. Wire one in, or leave it as the reference it is -- but do not read its presence as running code.

- `deployment`
- `evaluation`
- `governance`
- `observability`
- `provisioning`

### Identity at the edge

One bearer token, one service principal, one set of scopes: every caller acts as the same identity, so the audit names the service, not a person. Per-caller identity is an `access_model` decision nobody has answered; accept this or front the service with something that does.

### Facts this design stands on

The governance, the boundary and the topology follow from these values. A value learned from a person or inferred is asserted, not established -- confirm it with the client before the decision that rests on it stands.

- `data_residency = may_leave` -- interview -- asserted, not established: confirm before the decisions resting on it stand
- `hosting = customer-vpc` -- interview -- asserted, not established: confirm before the decisions resting on it stand

### Unanswered assumptions

Decisions were made without these facts. Each is a risk until somebody answers it (`fde ask`, or the interview), and the answer may change a decision.

- cheap_path_coverage: not stated, so nothing was decided on it
- confidence_calibrated: not stated, so nothing was decided on it
- latency_budget_ms: not stated, so nothing was decided on it
- sensitivity_present: not stated, so nothing was decided on it

### Gates waived

Each was blocking at build time. Somebody decided to proceed anyway, and this is who said what.

- **outcome_contract** (2026-09-20) -- no client owns an outcome: a public demonstration on CFPB complaint data; the baseline's business metric is stated, and nobody has set a target
  - covered: Nobody has agreed which number this system exists to move: no outcome contract was recorded.

## Decision debt

Everything the engagement rests on that nobody has settled, each with an owner and an age.

```text
complaints: decision debt as of 2026-10-12

  open (9)
    waiver         outcome_contract: no client owns an outcome: a public demonstration on CFPB complaint data; the baseline's business metric is stated, and nobody has set a target
                   owner: the author  22 day(s)
                   next: meet the gate, or restate the waiver if it still holds
    stated         accelerator = none: said by Atul Kapoor (admin), measurable but not measured
                   owner: admin
                   next: measure it: fde scan, or a document the client owns
    stated         existing_iac_tool = none: said by Atul Kapoor (admin), measurable but not measured
                   owner: admin
                   next: measure it: fde scan, or a document the client owns
    stated         container_competence = False: said by Atul Kapoor (admin), measurable but not measured
                   owner: admin
                   next: measure it: fde scan, or a document the client owns
    stated         existing_cluster = False: said by Atul Kapoor (admin), measurable but not measured
                   owner: admin
                   next: measure it: fde scan, or a document the client owns
    stated         provisioning_api = False: said by Atul Kapoor (admin), measurable but not measured
                   owner: admin
                   next: measure it: fde scan, or a document the client owns
    unsigned       data_access (2026-09-11)
                   owner: unsigned  31 day(s) AGING
                   next: re-record with --by, or leave it and know it
    unsigned       security_review (2026-09-11)
                   owner: unsigned  31 day(s) AGING
                   next: re-record with --by, or leave it and know it
    unheard        skeptic has never been asked
                   owner: skeptic
                   next: fde ask <eng> --role skeptic

9 item(s): 0 blocking the build, 0 blocking production, 2 older than 30 days, 2 unsigned
```

## What would stop this

The conditions on record under which the honest answer is to stop, judged against what has been measured so far.

```text
no stop conditions on record: fde stop-when <eng> --when "answered_accuracy < 0.88"
```

## The next decision

The single best next action judged from everything above, and what turns on it.

```text
next: fde implement project-0.1.27 --holdout engagements/complaints/artifacts/holdout.jsonl
  built -- drive it green, then run evals/acceptance.md with the client, and fde retro after the measurement window
```
