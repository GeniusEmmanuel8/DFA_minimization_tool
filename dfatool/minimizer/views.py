import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .dfa_core import minimize_dfa

logger = logging.getLogger(__name__)

# Limits keep one request from using unbounded CPU/memory (table filling grows ~ n^2).
MAX_BODY_BYTES = 200_000
MAX_STATES = 200
MAX_SYMBOLS = 50


def _validate_dfa(body):
    """Raise ValueError with a short message if the DFA JSON is malformed or too large."""
    if not isinstance(body, dict):
        raise ValueError("DFA must be a JSON object")
    for key in ("states", "alphabet", "start_state", "accept_states", "transitions"):
        if key not in body:
            raise ValueError(f"Missing field: {key}")
    if not isinstance(body["states"], list) or not isinstance(body["alphabet"], list):
        raise ValueError("states and alphabet must be lists")
    if not isinstance(body["accept_states"], list) or not isinstance(body["transitions"], dict):
        raise ValueError("accept_states must be a list and transitions an object")
    if not body["states"] or len(body["states"]) > MAX_STATES:
        raise ValueError(f"states must contain 1 to {MAX_STATES} entries")
    if not body["alphabet"] or len(body["alphabet"]) > MAX_SYMBOLS:
        raise ValueError(f"alphabet must contain 1 to {MAX_SYMBOLS} symbols")
    if body["start_state"] not in body["states"]:
        raise ValueError("start_state must be one of the states")
    if not set(body["accept_states"]) <= set(body["states"]):
        raise ValueError("accept_states must be a subset of states")
    for state in body["states"]:
        row = body["transitions"].get(state)
        if not isinstance(row, dict):
            raise ValueError(f"Missing transitions for state {state}")
        for symbol in body["alphabet"]:
            if row.get(symbol) not in body["states"]:
                raise ValueError(f"Transition {state} --{symbol}--> must lead to a known state")


# The API is stateless and has no login or cookies, so CSRF protection adds nothing here;
# cross-origin access is restricted by the CORS settings instead.
@csrf_exempt
def minimize_dfa_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    if len(request.body) > MAX_BODY_BYTES:
        return JsonResponse({"error": "Request too large"}, status=413)

    try:
        body = json.loads(request.body.decode("utf-8"))
        _validate_dfa(body)
        result = minimize_dfa(body)
        return JsonResponse(result)


        steps_json = [
            {
                "action": step.action,
                "pair": list(step.pair),
                "reason": step.reason,
                "dependent_on": [list(p) for p in step.dependent_on],
            }
            for step in result.steps
        ]

        minimized_json = {
            "states": result.minimized_dfa.states,
            "alphabet": result.minimized_dfa.alphabet,
            "start_state": result.minimized_dfa.start_state,
            "accept_states": list(result.minimized_dfa.accept_states),
            "transitions": result.minimized_dfa.transitions,
        }

        eq_classes_json = [list(c) for c in result.equivalent_classes]

        return JsonResponse({
            "steps": steps_json,
            "equivalence_classes": eq_classes_json,
            "minimized_dfa": minimized_json,
        })
    except (ValueError, TypeError, KeyError, UnicodeDecodeError) as e:
        # ValueError also covers invalid JSON; messages here are written by us, not internals
        return JsonResponse({"error": f"Invalid DFA: {e}" if isinstance(e, ValueError) else "Invalid DFA input"}, status=400)
    except Exception:
        logger.exception("Unexpected error while minimizing DFA")
        return JsonResponse({"error": "Internal error"}, status=500)
