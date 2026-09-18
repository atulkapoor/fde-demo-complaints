"""planning: optimisation, via plain-python.

Optimisation: output_shape == decision

Allocation subject to constraints, answered rather than guessed.

**A feasible answer or none.** That is what separates this from a model trained
to imitate past decisions: such a model will produce something plausible that
violates a constraint and will not mention that it did. Here, an infeasible
problem comes back infeasible, with the constraints that could not be satisfied
together.

The greedy assignment below is honest about being greedy -- it satisfies the
constraints and does not claim to be optimal. Where optimality matters, this is
the seam a real solver goes into, behind the same contract.
"""

from __future__ import annotations

from typing import Any

from app.contract import RefusedInput


class Infeasible(ValueError):
    """No assignment satisfies these constraints.

    Reported rather than approximated. An answer that quietly breaks a hard
    constraint is worse than no answer, because the breakage is discovered by
    whoever the constraint was protecting.
    """


class Planning:
    """Planner, as optimisation."""

    interface = "Planner"
    approach = "optimisation"
    stack = "plain-python"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Assign items to resources without exceeding capacity."""
        items = payload.get("items", [])
        capacity = payload.get("capacity", {})
        self._refuse_malformed(items, capacity)
        capacity = dict(capacity)
        assignment: dict[str, str] = {}

        for item in sorted(items, key=lambda i: -i.get("size", 1)):
            placed = False
            for resource, remaining in capacity.items():
                if remaining >= item.get("size", 1) and self._allowed(item, resource):
                    capacity[resource] = remaining - item.get("size", 1)
                    assignment[item["id"]] = resource
                    placed = True
                    break
            if not placed:
                raise Infeasible(
                    f"{item['id']} (size {item.get('size', 1)}) fits nowhere with "
                    f"remaining capacity {capacity}"
                )

        return {
            **payload,
            "plan": {
                "assignment": assignment,
                "remaining": capacity,
                "feasible": True,
                # Said plainly rather than implied. Feasible is a proof;
                # optimal is a claim this method cannot make.
                "optimal": False,
            },
        }

    @staticmethod
    def _refuse_malformed(items: Any, capacity: Any) -> None:
        """A type violation is refused at this door, not met as a TypeError
        halfway through the assignment."""
        def number(value: Any) -> bool:
            return isinstance(value, (int, float)) and not isinstance(value, bool)

        if not isinstance(items, list):
            raise RefusedInput("'items' must be a list")
        if not isinstance(capacity, dict) or not all(number(v) for v in capacity.values()):
            raise RefusedInput("'capacity' must be an object of resource -> number")
        for position, item in enumerate(items):
            if not isinstance(item, dict) or not isinstance(item.get("id"), (str, int)):
                raise RefusedInput(f"items[{position}] needs an 'id'")
            if not number(item.get("size", 1)):
                raise RefusedInput(f"items[{position}] 'size' must be a number")
            if not isinstance(item.get("allowed") or [], list):
                raise RefusedInput(f"items[{position}] 'allowed' must be a list")

    @staticmethod
    def _allowed(item: dict[str, Any], resource: str) -> bool:
        allowed = item.get("allowed")
        return resource in allowed if allowed else True
