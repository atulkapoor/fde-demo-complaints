"""Fail closed, by construction.

An approval gate that defaults to yes is decoration, and a critic that
defaults to silence is a rubber stamp. Both refuse until wired, so the first
run tells you what has not been decided yet -- instead of quietly doing the
irreversible thing. Both apply to ACTIONS: a request that asks nothing
outward passes untouched, one that does cannot pass unapproved.
"""


class NeedsApproval(RuntimeError):
    """A step that changes the world, with nobody having said yes."""


class CriticRejected(RuntimeError):
    """The check in front of an irreversible step said no."""


def is_action(payload) -> bool:
    """Whether this payload asks for something outward -- a tool call or
    a named action -- which is the only thing a gate has to say no to."""
    return isinstance(payload, dict) and ("tool" in payload or "action" in payload)


class ApprovalGate:
    """Sits in front of a step that changes something outside the system.

    Wire `approve` to a human or a policy. Idempotency is not this gate's
    job: the guarded step derives a key from the action itself and reserves
    it in app/ledger.py before acting, so a retry finds the key taken.
    """

    def __init__(self, guards, approve=None):
        self.guards = guards
        self._approve = approve

    def run(self, payload):
        if not is_action(payload):
            return payload
        if self._approve is None:
            raise NeedsApproval(
                f"{self.guards!r} changes the world and nothing approves it yet. "
                f"Construct this gate with approve=<callable> in pipeline.py."
            )
        if not self._approve(payload):
            raise NeedsApproval(f"approval for {self.guards!r} was refused")
        return payload


class Critic:
    """Sits in front of a step whose failure is an apology, not a rollback.

    Wire `review` to return a list of problems; an empty list lets the
    payload through. A mistake caught here becomes a regression case; one
    caught after becomes an apology.
    """

    def __init__(self, guards, review=None):
        self.guards = guards
        self._review = review

    def run(self, payload):
        if not is_action(payload):
            return payload
        if self._review is None:
            raise CriticRejected(
                f"{self.guards!r} is irreversible and nothing reviews it yet. "
                f"Construct this critic with review=<callable> in pipeline.py."
            )
        problems = self._review(payload)
        if problems:
            raise CriticRejected(f"{self.guards!r}: {problems}")
        return payload
