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

Here the decision is how a complaint closes: with an explanation, with
non-monetary relief, or with monetary relief. Every admissible outcome is
scored by the written signals below, the hard constraints drop the
inadmissible ones, and the best of what is left is returned with the signals
that fired -- so a wrong decision points at a rule somebody can read, not at a
weight nobody can.
"""

from __future__ import annotations

import re
from typing import Any

from app.contract import RefusedInput
from app.shapes import documents_of

EXPLANATION = "Closed with explanation"
NON_MONETARY = "Closed with non-monetary relief"
MONETARY = "Closed with monetary relief"

# Least relief first. A tie goes to the earlier outcome: relief is granted on
# evidence, never on a coin toss.
OUTCOMES = (EXPLANATION, NON_MONETARY, MONETARY)

# What the complaint is about decides how it closes far more often than how
# angrily it is written. Each signal is one question about the text, counted
# once however often it repeats -- a narrative that says "fee" forty times is
# not forty times more deserving. Every addition here is a decision somebody
# made and can defend, which is why there are few of them: a signal added to
# win one golden case is a memorised case with a regex for a disguise.
SIGNALS: dict[str, list[tuple[str, re.Pattern[str]]]] = {
    # A record to correct: credit files are fixed, blocked or deleted, and
    # nobody is paid.
    NON_MONETARY: [
        ("credit_report", re.compile(r"\bcredit (report|file|bureau)|\bconsumer report")),
        ("reporting", re.compile(r"\breporting\b")),
        ("fcra", re.compile(r"\bfair credit reporting\b|\bfcra\b|\b1681")),
        ("inaccurate", re.compile(r"\binaccura|\bincorrect")),
        ("privacy", re.compile(r"\bprivacy\b|\bpersonal information\b|\bwithout my\b")),
        ("identity_theft", re.compile(r"\bidentity theft\b|\bfraudulent (account|inquir)")),
        ("removal", re.compile(r"\b(remov|delet)")),
        ("bureau", re.compile(r"\b(equifax|transunion|experian)\b")),
    ],
    # Money the company took and can give back: fees, interest, charges.
    MONETARY: [
        ("fee", re.compile(r"\bfees?\b|\boverdraft")),
        ("interest", re.compile(r"\binterest\b")),
        ("refund", re.compile(r"\brefund|\breimburs")),
        ("charge", re.compile(r"\b(over)?charg(e|ed|es)\b")),
        ("card", re.compile(r"\b(credit|debit|gift) card\b")),
        ("bonus", re.compile(r"\bbonus")),
        ("amount", re.compile(r"\$\s?\d")),
    ],
    # Disputes about what is owed and on what terms: the company's usual
    # answer is its own account of the contract.
    EXPLANATION: [
        ("mortgage", re.compile(r"\bmortgage|\bescrow\b|\bforbearance\b|\bheloc\b|\bforeclos")),
        ("loan", re.compile(r"\bloans?\b")),
        ("debt", re.compile(r"\bdebts?\b|\bcollections?\b|\bcollector")),
        ("property", re.compile(r"\bproperty\b")),
    ],
}

# Something a company could pay back. Without it monetary relief is not a
# decision about this complaint at all.
MONEY = re.compile(r"\$\s?\d|\bfees?\b|\bcharg|\brefund|\bpa(y|id)|\bfunds?\b|\bmoney\b|\bbalance\b")

# Redaction marks (XXXX, XX/XX/XXXX) are not words.
REDACTION = re.compile(r"\bx{2,}\b")


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

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = self._complaint(payload)
        constraints = [
            {"name": "known_outcome",
             "holds": lambda d: d.get("decision") in OUTCOMES},
            {"name": "monetary_relief_needs_money",
             "holds": lambda d: d.get("decision") != MONETARY or bool(MONEY.search(text))},
        ]

        fired = {outcome: [name for name, pattern in SIGNALS[outcome] if pattern.search(text)]
                 for outcome in OUTCOMES}
        admissible = [o for o in OUTCOMES
                      if all(c["holds"]({"decision": o}) for c in constraints)]
        # max() keeps the first of equals, and OUTCOMES is least relief first.
        decision = {"decision": max(admissible, key=lambda o: len(fired[o]))}
        self.check(decision, constraints)
        return {
            **payload,
            "decision": decision,
            "feasible": True,
            "constraints_checked": [c["name"] for c in constraints],
            # Exhaustive over three outcomes, so best under the signals above.
            # That is a statement about the rules, not about the complaint.
            "optimal": True,
            "trace": {"signals": fired, "admissible": admissible},
        }

    @staticmethod
    def _complaint(payload: dict[str, Any]) -> str:
        """The one complaint this request is about, lowercased."""
        documents = documents_of(payload)
        if len(documents) != 1:
            # Five complaints answered with one decision is an answer nobody
            # can trace to a complaint.
            raise RefusedInput(
                f"one complaint per request, not {len(documents)} documents"
            )
        text = documents[0]["text"].lower()
        if not re.search(r"[a-z]{2,}", REDACTION.sub(" ", text)):
            raise RefusedInput("the complaint has no words to decide on")
        return text
