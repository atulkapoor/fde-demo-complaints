"""reasoning: optimisation-reasoning, via plain-python.

Constraint optimisation as the decision-maker: output_shape == decision

A decision produced by a solver rather than a prediction dressed as one.

The distinction is the point. Optimisation makes decisions; machine learning
makes predictions. A model trained to imitate past decisions will produce
something that looks like one and violates a constraint without mentioning it,
because nothing in its output represents feasibility.

The two combine well and the order matters: predict demand, then optimise
against the prediction. The prediction is an input to the decision and never the
decision itself, and a system that treats them as the same thing has no way to
say which part was wrong when the answer is bad.
"""

from __future__ import annotations

from typing import Any

from app.contract import DECISIONS, MONETARY_RELIEF, NON_MONETARY_RELIEF


class ConstraintViolated(ValueError):
    """A proposed answer breaks a hard constraint."""


class Reasoning:
    """Generator, as optimisation-reasoning."""

    interface = "Generator"
    approach = "optimisation-reasoning"
    stack = "plain-python"

    def check(self, decision: dict[str, Any], constraints: list[dict[str, Any]]) -> None:
        """Verify before returning, not after acting.

        This is what a predictive model cannot do for you: state whether the
        answer is admissible, separately from whether it looks right.
        """
        broken = [c["name"] for c in constraints if not c["holds"](decision)]
        if broken:
            raise ConstraintViolated(
                f"{broken} are not satisfied by this decision; a plausible answer "
                f"that breaks a hard constraint is worse than no answer"
            )

    @staticmethod
    def constraints(evidence: dict[str, list[str]]) -> list[dict[str, Any]]:
        """The hard rules, held against the complaint's own words rather than
        against however the planner happened to rank the outcomes."""
        return [
            {"name": "decision_is_on_the_contract",
             "holds": lambda d: d.get("decision") in DECISIONS},
            # Money goes out only where the complaint says money was lost.
            {"name": "monetary_relief_has_money_at_stake",
             "holds": lambda d: d.get("decision") != MONETARY_RELIEF
             or bool(evidence.get("money"))},
            # A record is corrected only where the complaint names one.
            {"name": "non_monetary_relief_has_something_to_correct",
             "holds": lambda d: d.get("decision") != NON_MONETARY_RELIEF
             or bool(evidence.get("correction"))},
        ]

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        # Perception admits exactly one complaint, so there is one decision.
        (record,) = payload["mapping"]
        decision = record["mapped"]
        constraints = self.constraints(payload["evidence"][record["id"]])
        self.check(decision, constraints)
        return {
            **payload,
            "decision": decision,
            "feasible": True,
            "constraints_checked": [c["name"] for c in constraints],
            # Proven admissible; not claimed best. Those are different results
            # and only one of them this can demonstrate.
            "optimal": False,
        }
