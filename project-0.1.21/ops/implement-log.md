# Implementation log

## Round 1

- check: red
- changed: app/components/planning.py, app/components/reasoning.py

```
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
{"failed_step": "reasoning", "request_id": "local"}
84 golden case(s) errored -- the pipeline is not yet implemented end to end
```

## Round 2

- check: green

```
               by field:  {'decision': 26}
               - {"id": "complaint-049", "source": "prediction", "missed": ["decision"], "invented": []}
               - {"id": "complaint-030", "source": "prediction", "missed": ["decision"], "invented": []}
               - {"id": "complaint-055", "source": "prediction", "missed": ["decision"], "invented": []}
               - {"id": "complaint-045", "source": "prediction", "missed": ["decision"], "invented": []}
               - {"id": "complaint-037", "source": "prediction", "missed": ["decision"], "invented": []}
               - {"id": "complaint-011", "source": "prediction", "missed": ["decision"], "invented": []}
               - {"id": "complaint-054", "source": "prediction", "missed": ["decision"], "invented": []}
               - {"id": "complaint-016", "source": "prediction", "missed": ["decision"], "invented": []}
               - {"id": "complaint-047", "source": "prediction", "missed": ["decision"], "invented": []}
               - {"id": "complaint-056", "source": "prediction", "missed": ["decision"], "invented": []}
  edge_case       0 cases  --
  adversarial     2 cases  100.0%
{"level": "warning", "ledger": "STATE_DIR unset: audit and idempotency live in process memory and vanish on restart"}
note: the edge-case layer is empty -- the happy path is all that was measured
holdout: green (cases the implementer never saw)
```

**Stopped by**: harness green.
