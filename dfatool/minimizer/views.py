from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .dfa_core import minimize_dfa


@csrf_exempt
def minimize_dfa_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
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
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
