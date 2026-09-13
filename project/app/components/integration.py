"""integration: governed-tools, via plain-python.

Governed tool boundary: external_systems > 1

One entry point through which every outward call passes. Past the first system
this stops being tidiness -- it is the only place authentication, authorisation
and audit can be enforced once rather than per caller.

**Annotations describe; this enforces.** A tool declares what it is --
read-only, destructive, idempotent, reaching outside a closed world -- and those
declarations shape how a call is framed to a person. They are the tool's own
claim about itself, so nothing here trusts them as policy: an unregistered tool
cannot be called at all, and a declaration that a call is safe does not make it
so.

**Destructive is assumed unless declared otherwise**, because the failure of
guessing wrong in that direction is recoverable and the other is not.

**Reversibility is a separate axis from destructiveness.** Moving something to
a trash folder is destructive and reversible; deleting it permanently is both.
Collapsing the two loses exactly the distinction that decides whether a critic
is needed before the call.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from app.contract import MONETARY_RELIEF


class UnregisteredTool(LookupError):
    """Called something the boundary does not know about.

    Not a lookup miss to be handled quietly: the point of a single entry is that
    nothing else has a way out, so this means something tried to route around it.
    """


class ScopeDenied(PermissionError):
    """The caller's authority does not cover this tool."""


@dataclass(frozen=True)
class Tool:
    """A declared capability.

    The declarations mirror the tool-annotation vocabulary in general use, so a
    client that understands them can frame a call sensibly. They are hints from
    the tool about itself, and are never the thing that grants permission.
    """

    name: str
    run: Callable[..., Any]
    required_scope: str
    input_schema: dict[str, Any] = field(default_factory=dict)

    read_only: bool = False
    # Assumed destructive. Guessing wrong this way costs a confirmation;
    # guessing wrong the other way costs the data.
    destructive: bool = True
    idempotent: bool = False
    # Reaches systems outside the closed world of this deployment.
    open_world: bool = True
    # Separate from destructive on purpose: trash is destructive and
    # reversible, permanent deletion is destructive and not.
    reversible: bool = False

    @property
    def mutative(self) -> bool:
        """Whether this changes anything. What the autonomy gate keys on."""
        return not self.read_only


class RecordingSystem:
    """An outside system as this boundary sees it: something that takes a request.

    Stands in for the client's CRM, billing and letters systems and keeps what
    each was asked to do. The real clients replace these behind the same tool
    names and scopes; nothing in front of the boundary changes when they do.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.received: list[dict[str, Any]] = []

    def __call__(self, **arguments: Any) -> dict[str, Any]:
        self.received.append(arguments)
        return {"system": self.name, "accepted": True}


def decision_tools() -> list[Tool]:
    """The three systems a decision reaches."""
    return [
        # A CRM entry can be amended: mutative, not destructive, reversible.
        Tool("crm.record_decision", RecordingSystem("crm"), "crm:write",
             destructive=False, idempotent=True, reversible=True),
        # A letter, once sent, stays sent.
        Tool("letters.send_decision", RecordingSystem("letters"), "letters:send",
             destructive=False, idempotent=True, reversible=False),
        # Money that has left does not come back by asking for it.
        Tool("billing.open_relief", RecordingSystem("billing"), "billing:credit",
             idempotent=True, reversible=False),
    ]


def reaches(decision: str) -> list[str]:
    """The systems a decision reaches. Billing only when money moves."""
    tools = ["crm.record_decision", "letters.send_decision"]
    if decision == MONETARY_RELIEF:
        tools.append("billing.open_relief")
    return tools


class Integration:
    """ToolBoundary, as governed-tools."""

    interface = "ToolBoundary"
    approach = "governed-tools"
    stack = "plain-python"

    def __init__(self, tools: list[Tool] | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        self.audit: list[dict[str, Any]] = []
        # Keyed actions already carried out, and what each returned.
        self._completed: dict[str, dict[str, Any]] = {}
        for tool in (decision_tools() if tools is None else tools):
            self.register(tool)

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def call(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        subject: str,
        granted_scopes: set[str],
        actor: str | None = None,
    ) -> Any:
        """Make an outward call, or refuse to.

        `subject` is the person the call is made for; `actor` is what made it.
        The audit names the subject, because a record saying an agent issued a
        refund has lost the chain that makes it useful.
        """
        tool = self._tools.get(name)
        if tool is None:
            raise UnregisteredTool(
                f"{name!r} is not registered; every outward call goes through here"
            )

        # Authority is checked here, against what the caller actually holds --
        # never against what the tool says about itself.
        if tool.required_scope not in granted_scopes:
            raise ScopeDenied(
                f"{name!r} needs {tool.required_scope!r}, which {subject} does not hold"
            )

        self._record("intent", tool, subject, actor, arguments)
        try:
            result = tool.run(**arguments)
        except Exception as exc:
            self._record("failed", tool, subject, actor, arguments, error=str(exc))
            raise
        self._record("outcome", tool, subject, actor, arguments)
        return result

    def mutative_tools(self) -> list[str]:
        """What needs a gate and an idempotency key."""
        return sorted(n for n, t in self._tools.items() if t.mutative)

    def irreversible_tools(self) -> list[str]:
        """What needs a critic in front of it."""
        return sorted(n for n, t in self._tools.items() if t.mutative and not t.reversible)

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Carry one approved decision to every system it reaches, once.

        The gate's idempotency key joined to the complaint names the action, so
        running the same complaint again returns the decision already carried
        out instead of sending a second letter or opening a second credit.
        """
        decision = payload["decision"]
        key = f"{payload['idempotency_key']}:{payload['complaint_id']}"
        if key not in self._completed:
            arguments = {"complaint_id": payload["complaint_id"],
                         "decision": decision["decision"], "idempotency_key": key}
            for name in reaches(decision["decision"]):
                self.call(
                    name,
                    arguments,
                    subject=payload["subject"],
                    granted_scopes=set(payload.get("granted_scopes", [])),
                    actor=payload.get("actor"),
                )
            self._completed[key] = dict(decision)
        return dict(self._completed[key])

    def _record(self, phase, tool, subject, actor, arguments, error=None) -> None:
        self.audit.append({
            "phase": phase,
            "tool": tool.name,
            # The human is the subject; the agent is the actor. Not the reverse.
            "subject": subject,
            "actor": actor,
            "destructive": tool.destructive,
            "reversible": tool.reversible,
            "argument_keys": sorted(arguments),
            "error": error,
        })
