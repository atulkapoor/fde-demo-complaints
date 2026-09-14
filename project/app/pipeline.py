"""The order things run in.

Ordered by what caps what: a step whose quality bounds another comes
first, so when an answer is wrong there is somewhere to look.
Approval gates and critics are steps like any other -- removing one
is a visible diff, not an oversight.

Only payload-transforming components are chained here. Deployment,
provisioning, evaluation and their kin are decided and emitted, but a
service unit is not a step a payload passes through.

The evaluation harness calls run() with each golden case's raw input.
Adapting that input to the first step's payload shape is yours: do it
at the top of run(), where the seam is visible.
"""

import hashlib

from app import controls
from app.components import integration
from app.components import perception
from app.components import planning
from app.components import reasoning
from app.components import representation
from app.contract import DECISIONS, MONETARY_RELIEF, NON_MONETARY_RELIEF, RefusedInput

IDEMPOTENCY_KEY = '1224ad29445b9354'

# One operating team acts here, and it holds every scope a decision needs.
GRANTED_SCOPES = ('crm:write', 'letters:send', 'billing:credit')


def approve_integration(case):
    """The operating team's standing approval, since nobody waits on a decision.

    Yes to a decision reasoning proved admissible, carried under this gate's
    key. No to anything else, which then waits for a person.
    """
    return (
        case.get('feasible') is True
        and bool(case.get('constraints_checked'))
        and case.get('decision', {}).get('decision') in DECISIONS
        and case.get('idempotency_key') == IDEMPOTENCY_KEY
    )


def review_integration(case):
    """What would turn the letter or the credit into an apology."""
    problems = []
    if case.get('needs_attention'):
        problems.append(f"the mapper could not finish {case['needs_attention']}")
    decision = case.get('decision', {}).get('decision')
    evidence = case.get('evidence', {}).get(case.get('complaint_id'), {})
    if decision == MONETARY_RELIEF and not evidence.get('money'):
        problems.append('monetary relief, and the complaint puts no money at stake')
    if decision == NON_MONETARY_RELIEF and not evidence.get('correction'):
        problems.append('non-monetary relief, and the complaint names nothing to correct')
    return problems


STEPS = [
    ('perception', perception.Perception()),
    ('planning', planning.Planning()),
    ('representation', representation.Representation()),
    ('reasoning', reasoning.Reasoning()),
    ('approve-integration', controls.ApprovalGate(guards='integration', idempotency_key=IDEMPOTENCY_KEY, approve=approve_integration)),
    ('critic-integration', controls.Critic(guards='integration', review=review_integration)),
    ('integration', integration.Integration()),
]


def run(payload):
    # The harness, like the intake feed, hands over a complaint's narrative as
    # bare text. Its id is its digest, so the same complaint run twice is the
    # same action -- which is what the idempotency key needs to mean anything.
    if not isinstance(payload, str):
        raise RefusedInput(f'a complaint arrives as text, not {type(payload).__name__}')
    complaint_id = hashlib.sha256(payload.encode()).hexdigest()[:16]
    payload = {
        'complaint_id': complaint_id,
        'documents': [{'id': complaint_id, 'text': payload}],
        'idempotency_key': IDEMPOTENCY_KEY,
        # The person the decision is made for, and the thing acting for them.
        'subject': f'complainant:{complaint_id}',
        'actor': 'complaints-pipeline',
        'granted_scopes': list(GRANTED_SCOPES),
    }
    for name, step in STEPS:
        payload = step.run(payload)
    return payload


# Backported from fde-framework 0.1.11: the deployment runs
# `python -m app.pipeline`, and a module that defines functions and
# exits is a service that dies silently. This is the service.
if __name__ == "__main__":
    # Post-measurement ops hardening, updated to the 0.1.13 emission
    # (threaded server, read deadlines, body cap, catch-all 500s,
    # loopback bind by default) -- after the measured runs, labelled.
    import json as _json
    import os as _os
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    from app.contract import RefusedInput

    MAX_BODY = int(_os.environ.get("MAX_BODY_BYTES", str(10 * 1024 * 1024)))

    class _Handler(BaseHTTPRequestHandler):
        # A slow or malicious socket must cost one thread and one
        # deadline, never the service.
        timeout = 30
        def _send(self, code, body):
            data = _json.dumps(body, default=str).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self._send(200, {"status": "ok"})
            else:
                self._send(404, {"error": "POST / with a JSON payload"})

        def do_POST(self):
            if self.path != "/":
                self._send(404, {"error": "POST / with a JSON payload"})
                return
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                self._send(411, {"error": "Content-Length required"})
                return
            try:
                length = int(raw_length)
            except ValueError:
                self._send(400, {"error": "Content-Length is not a number"})
                return
            if length < 0 or length > MAX_BODY:
                self._send(413, {"error": "body too large"})
                return
            try:
                payload = _json.loads(self.rfile.read(length) or b"null")
            except ValueError:
                self._send(400, {"error": "body is not JSON"})
                return
            try:
                self._send(200, {"result": run(payload)})
            except RefusedInput as refusal:
                self._send(422, {"refused": str(refusal)})
            except Exception as exc:  # noqa: BLE001
                # A dropped connection tells the caller nothing; a
                # 500 with the exception NAME (never a traceback)
                # is a diagnosable failure.
                self._send(500, {"error": type(exc).__name__,
                                 "detail": str(exc)[:200]})

        def log_message(self, fmt, *args):
            print(fmt % args)

    port = int(_os.environ.get("PORT", "8080"))
    # Loopback by default: exposing the port is a deployment
    # decision made in the unit file (Environment=BIND=...),
    # never a default the code took alone.
    bind = _os.environ.get("BIND", "127.0.0.1")
    print(f"serving on {bind}:{port} -- /health, POST /")
    ThreadingHTTPServer((bind, port), _Handler).serve_forever()
