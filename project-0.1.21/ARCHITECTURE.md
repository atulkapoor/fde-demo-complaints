# Architecture

Topology: **customer-vpc**  
Fingerprint: `5af0574c76b4e4db`

## Scope

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

## Decisions

| Component | Approach | Implemented with | Why |
|---|---|---|---|
| deployment | systemd-unit (advisory: decided and emitted, not a payload step) | plain-python | Service unit: always |
| evaluation | labelled-metrics (advisory: decided and emitted, not a payload step) | plain-python | Labelled metrics: output_shape == decision |
| governance | audit-only (advisory: decided and emitted, not a payload step) | plain-python | Audit trail: data_residency == may_leave |
| integration | governed-tools | plain-python | Governed tool boundary: external_systems > 1 |
| observability | traced (advisory: decided and emitted, not a payload step) | plain-python | Distributed tracing: always |
| perception | text-extraction | plain-python | Text extraction: input_format == text |
| planning | optimisation | plain-python | Optimisation: output_shape == decision |
| provisioning | ansible-playbook (advisory: decided and emitted, not a payload step) | plain-python | Convergent configuration: provisioning_api == false |
| reasoning | optimisation-reasoning | plain-python | Constraint optimisation as the decision-maker: output_shape == decision |
| representation | deterministic | plain-python | Deterministic: output_shape == decision |

The tool boundary is emitted UNWIRED: no external system's tools are registered and the approval gate and critic are constructed without `approve=`/`review=`. Until the implementation registers tools and wires both, every action-shaped request is refused (409) -- fail closed, by design.

## Tools and libraries

| Component | Chosen | Licence | Alternatives in this topology |
|---|---|---|---|
| deployment | plain-python | PSF | -- |
| evaluation | plain-python | PSF | xgboost |
| governance | plain-python | PSF | -- |
| integration | plain-python | PSF | mcp |
| observability | plain-python | PSF | opentelemetry |
| perception | plain-python | PSF | -- |
| planning | plain-python | PSF | ortools |
| provisioning | plain-python | PSF | -- |
| reasoning | plain-python | PSF | ortools |
| representation | plain-python | PSF | -- |

Adopting an alternative the client already operates: `fde reuse <engagement> <stack>` and rebuild -- the architecture does not change, only the emitted code does.

## Agent and tool posture

- `integration` acts on the world. In front of it: approve-integration, critic-integration; an idempotency key derived from each action and reserved in the ledger (app/ledger.py) before it runs, so a retry cannot act twice.
- One operating team acts here; the audit names people, not roles.
- Tool boundary realized via `plain-python`.


## Rejected alternatives

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
- `fixed-sequence` -- ruled out by output_shape == decision
- `model-planner` -- optimisation is simpler and applies here

**provisioning**
- `gitops` -- ruled out by existing_cluster == false
- `terraform-module` -- ruled out by provisioning_api == false
- `manual-runbook` -- ansible-playbook is simpler and applies here

**reasoning**
- `cascade` -- nothing here matches confidence_calibrated == true and cheap_path_coverage < 0.95 -- unanswered: cheap_path_coverage, confidence_calibrated (an answer could admit it)
- `classical-ml` -- nothing here matches output_shape == classification or output_shape == ranking or output_shape == decision and labelled_count >= 1000
- `finetune` -- ruled out by output_shape == decision
- `llm` -- ruled out by output_shape == decision

**representation**
- `assisted-deterministic` -- nothing here matches output_shape == structured and cheap_path_coverage < 0.95 and interpretability_required == true or output_shape == decision and cheap_path_coverage < 0.95 -- unanswered: cheap_path_coverage (an answer could admit it)
- `cascade` -- nothing here matches confidence_calibrated == true and cheap_path_coverage < 0.95 -- unanswered: cheap_path_coverage, confidence_calibrated (an answer could admit it)
- `classical-ml` -- nothing here matches output_shape == classification or output_shape == ranking or output_shape == decision and labelled_count >= 1000
- `finetune` -- ruled out by output_shape == decision
- `llm-extraction` -- nothing here matches output_shape == structured
- `segmentation` -- nothing here matches output_shape == freeform

## Assumptions

Nobody answered these, so nothing was decided on them. Each is a question worth asking before this is built.

- cheap_path_coverage: not stated, so nothing was decided on it
- confidence_calibrated: not stated, so nothing was decided on it
- latency_budget_ms: not stated, so nothing was decided on it
- sensitivity_present: not stated, so nothing was decided on it

## Licences

Everything this design pulls in, so it can be checked before a legal team checks it.

- `plain-python`: PSF
