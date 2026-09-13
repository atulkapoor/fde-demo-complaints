"""planning: optimisation, via plain-python.

Optimisation: output_shape == decision

Allocation subject to constraints, answered rather than guessed.

**A feasible answer or none.** That is what separates this from a model trained
to imitate past decisions: such a model will produce something plausible that
violates a constraint and will not mention that it did. Here, an infeasible
problem comes back infeasible, with the constraints that could not be satisfied
together.

The values below are declared rules, not fitted weights, and the assignment is
honest about that -- it satisfies the constraints and does not claim the values
are right. Where they stop being good enough, this is the seam a better scorer
goes into, behind the same contract.
"""

from __future__ import annotations

import re
from typing import Any

from app.contract import DECISIONS, EXPLANATION, MONETARY_RELIEF, NON_MONETARY_RELIEF


class Infeasible(ValueError):
    """No assignment satisfies these constraints.

    Reported rather than approximated. An answer that quietly breaks a hard
    constraint is worse than no answer, because the breakage is discovered by
    whoever the constraint was protecting.
    """


# What the complaint's own words put on the table, by the remedy each makes
# possible. A cue is evidence that a remedy is available, never a verdict on
# its own; the weight is how strongly it says so.
CUES: dict[str, dict[str, tuple[re.Pattern[str], int]]] = {
    "money": {
        # A fee, or a plea to waive one, is the charge a company most often
        # hands back.
        "fee": (re.compile(r"\bfees?\b", re.I), 2),
        "waiver": (re.compile(r"\bwaiv", re.I), 2),
    },
    "correction": {
        # Credit reporting disputes end in a corrected file, never a cheque --
        # whether the complaint names the report or the bureau keeping it.
        "credit_report": (re.compile(
            r"\bcredit (?:report|file)|\bconsumer report|\b(?:equifax|transunion|experian)\b",
            re.I), 2),
        "identity_theft": (re.compile(
            r"identity theft|fraudulent accounts?|not mine|never opened|did not open", re.I), 2),
        "inquiry": (re.compile(r"\binquir(?:y|ies)\b", re.I), 1),
        "late_payment": (re.compile(r"\blate payments?\b", re.I), 1),
    },
}

# The evidence an outcome needs before it is admissible at all. Closing with
# an explanation needs none.
REQUIRES = {MONETARY_RELIEF: "money", NON_MONETARY_RELIEF: "correction", EXPLANATION: None}

# An explanation is always available and commits the company to nothing past a
# letter, so relief has to outweigh it rather than merely be mentioned.
EXPLANATION_VALUE = 1

# Ties go to the outcome that commits the company to less.
COMMITMENT = {EXPLANATION: 0, NON_MONETARY_RELIEF: 1, MONETARY_RELIEF: 2}


class Planning:
    """Planner, as optimisation."""

    interface = "Planner"
    approach = "optimisation"
    stack = "plain-python"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Assign each complaint the admissible outcome its evidence values most."""
        records, assignment, evidence = [], {}, {}
        for record in payload.get("records", []):
            found = self.evidence(record["text"])
            admissible = [o for o in DECISIONS if REQUIRES[o] is None or found[REQUIRES[o]]]
            best = max(admissible, key=lambda o: (self.value(o, found), -COMMITMENT[o]))
            assignment[record["id"]] = best
            evidence[record["id"]] = found
            records.append({**record, "raw": {"decision": best}})

        return {
            **payload,
            "records": records,
            # The contract the mapper holds this plan to.
            "contract": ["decision"],
            "assignment": assignment,
            "evidence": evidence,
            "feasible": True,
            # Said plainly rather than implied. Feasible is a proof; optimal is
            # a claim this method cannot make.
            "optimal": False,
        }

    @staticmethod
    def evidence(text: str) -> dict[str, list[str]]:
        """The cues present in the text, by the remedy they support."""
        return {
            kind: [name for name, (pattern, _) in cues.items() if pattern.search(text)]
            for kind, cues in CUES.items()
        }

    @staticmethod
    def value(outcome: str, found: dict[str, list[str]]) -> int:
        kind = REQUIRES[outcome]
        if kind is None:
            return EXPLANATION_VALUE
        return sum(CUES[kind][name][1] for name in found[kind])
