"""perception: text-extraction, via plain-python.

Text extraction: input_format == text

This sets the ceiling for everything downstream, and it is the most
under-invested part of most systems. A badly parsed table is not recovered by a
better reranker or a better model -- the relationship between the numbers is
already gone.

So the job here is not only to extract. It is to **say what was lost**. A parser
that flattens a table silently sets a limit nobody discovers until the answers
are wrong; one that reports the flattening turns a mystery into a number an
engineer can quote before promising anything.

Tables are the usual casualty. A row of figures collapsed into a line has kept
every value and thrown away which column each belonged to, which is exactly the
part that mattered.
"""

from __future__ import annotations

import re
from typing import Any

from app.contract import RefusedInput

# Lines that look like a row of a table: repeated separators with content
# between them. Crude, and enough to notice that structure was present.
TABULAR = re.compile(r"(\S+\s*[|\t]\s*){2,}\S+")

# Runs of whitespace used as column separation rather than as spacing.
COLUMNAR = re.compile(r"\S+ {3,}\S+ {3,}\S+")

# The corpus redacts names, numbers and dates to runs of X. Those are the
# redactor's marks, not the complainant's words.
REDACTION = re.compile(r"X{2,}")


class Perception:
    """Parser, as text-extraction."""

    interface = "Parser"
    approach = "text-extraction"
    stack = "plain-python"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        documents = payload.get("documents") if isinstance(payload, dict) else None
        # One complaint, one decision. Deciding on none invents a complaint;
        # picking one of several is a guess nobody can trace.
        if not isinstance(documents, list) or len(documents) != 1:
            raise RefusedInput(
                f"expected exactly one complaint document, got {documents!r:.80}"
            )
        records = [self._read(d) for d in documents]
        clean = [r for r in records if not r["losses"]]
        return {
            **payload,
            "records": records,
            # One number to quote before promising anything downstream. If this
            # is 0.6, no amount of work further along gets the system past it.
            "clean_share": len(clean) / (len(records) or 1),
        }

    def _read(self, document: dict[str, Any]) -> dict[str, Any]:
        text = document.get("text") if isinstance(document, dict) else None
        if not isinstance(text, str):
            raise RefusedInput(
                f"a document's text must be a string, not {type(text).__name__}"
            )
        if not re.search(r"[A-Za-z0-9]", REDACTION.sub("", text)):
            raise RefusedInput(
                "empty document: nothing is left once whitespace and redaction "
                "marks are removed"
            )
        losses = []

        tabular_lines = [ln for ln in text.splitlines() if TABULAR.search(ln)]
        columnar_lines = [ln for ln in text.splitlines() if COLUMNAR.search(ln)]

        if tabular_lines:
            losses.append({
                "kind": "table_flattened",
                "lines": len(tabular_lines),
                "detail": "row structure present in the source and not preserved here; "
                          "column membership is lost, and nothing downstream restores it",
            })
        if columnar_lines and not tabular_lines:
            losses.append({
                "kind": "columns_inferred_from_spacing",
                "lines": len(columnar_lines),
                "detail": "alignment suggests columns; whitespace is not a reliable "
                          "separator and this may have merged or split fields",
            })

        return {
            "id": document.get("id"),
            "text": self._normalise(text),
            "losses": losses,
            # Not a model's confidence. A structural observation: how much of
            # this document arrived in a shape we can stand behind.
            "usable": not losses,
        }

    @staticmethod
    def _normalise(text: str) -> str:
        """Whitespace tidied, line structure kept.

        Line breaks are load-bearing in documents -- collapsing them is the
        second most common way a parser destroys what it was given.
        """
        return "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines())
