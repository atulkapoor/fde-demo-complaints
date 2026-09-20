# Scorecard

**17 of 22 measured properties hold.** Measured on `/Users/atulkapoor/Documents/fde-demo-complaints/project-0.1.27`. A property this build cannot measure is marked n/a, never counted as held. The service was booted on the machine that ran this card, not inside the deployed unit; the out-of-sample rows (holdout, external exam, generalisation gap, the baseline's bar) are the fitness rows, the rest are self-consistency.

| Property | Measured | Holds |
|---|---|---|
| own tests | 7 passed in 1.32s | yes |
| lint | clean | yes |
| exam: golden | 94.8% on 96 cases (majority 43.8%; abstained 1.0%, 95.8% on the answered; in-sample: the baseline is fitted on this file) | yes |
| exam: edge_case | 42.9% on 7 cases (majority 57.1%) | **no** |
| exam: adversarial | 45.5% on 11 cases (0 followed, 6 on misread bases) | **no** |
| exam: verdict | the attack layer found takers -- 0 injection(s) followed, 6 answered wrong regardless of the injection (the base case is misread un-steered), 0 answered wrong u | **no** |
| exam record | every eval file matches its recorded digest | yes |
| holdout | 73.9% on 46 cases (majority 41.3%; abstained 2.2%, 75.6% on the answered) | yes |
| holdout: sample size | 46 cases | yes |
| holdout: the file on record | matches evals/manifest.json | yes |
| generalisation gap | golden 94.8% - holdout 73.9% = +20.9% | **no** |
| beats the baseline error rate | 75.6% on the answered against a recorded first-pass accuracy of 94.0%, abstaining 2.2% | **no** |
| external exam | not given | n/a |
| edge: boots | answers /health | yes |
| edge: identity | 401 without a token | yes |
| edge: forged result | 422 | yes |
| edge: forged identity | 422 | yes |
| edge: malformed body | 400 | yes |
| edge: a valid request | 200 "Closed with explanation" | yes |
| edge: the answer says why | yes | yes |
| edge: readiness | 200 ready | yes |
| risk register: scaffolds | none | yes |
| risk register: gates waived | none | n/a |
| risk register: asserted facts | 2 boundary-bearing fact(s) asserted | n/a |
| environment | every variable the code reads is documented | yes |
| training path | none in this build | n/a |
| regression from the last card | no previous card | n/a |

## Not holding

- **exam: edge_case**: 42.9% on 7 cases (majority 57.1%)
- **exam: adversarial**: 45.5% on 11 cases (0 followed, 6 on misread bases)
- **exam: verdict**: the attack layer found takers -- 0 injection(s) followed, 6 answered wrong regardless of the injection (the base case is misread un-steered), 0 answered wrong u -- the harness's own exit status at --min-score 0.0
- **generalisation gap**: golden 94.8% - holdout 73.9% = +20.9% -- past 20% the golden score describes the exam, not the system; a component that reads the holdout file defeats this row, which is what --external is for
- **beats the baseline error rate**: 75.6% on the answered against a recorded first-pass accuracy of 94.0%, abstaining 2.2% -- evals/acceptance.md: the baseline's error rate is the number to beat; measured on what the system answered, with the abstained share beside it

## Notes

- own tests: the deliverable's own smoke and edge tests, model-free
- holdout: cases the delivery never shipped; the harness's holdout floor applies
- holdout: sample size: the protocol's floor for a blind sample is 30; the acceptance run itself is sized to the golden set
- external exam: a second out-of-sample set (--external <jsonl>), e.g. the client's own later export; a component that memorises the holdout file scores 100% there and single digits here
- edge: identity: no token, no service, with a request id
- edge: forged result: a caller cannot hand the pipeline its own answer
- edge: a valid request: the exam's own first case through the edge; refusals alone proved a service that failed every real request
- edge: the answer says why: an answer names what it stood on: scores and carrying tokens, cited evidence, or who decided
- edge: readiness: judged where nothing external is needed; with a model seam it depends on the deployment's endpoint and is reported only
- risk register: scaffolds: a scaffold raises on use; a green exam cannot include it
- risk register: gates waived: reported, not judged: a waiver is the engagement's decision, on the record
- risk register: asserted facts: reported: confirm each with the client before the decisions resting on it stand
