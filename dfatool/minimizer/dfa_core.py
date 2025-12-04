from collections import defaultdict, deque

def minimize_dfa(dfa):

    # unpack DFA 
    states = list(dfa["states"])
    alphabet = list(dfa["alphabet"])
    start = dfa["start_state"]
    accept = set(dfa["accept_states"])
    trans = dfa["transitions"]

    steps = []  # logs for your UI

    #  remove unreachable states
    reachable = set()
    q = deque([start])
    reachable.add(start)

    while q:
        s = q.popleft()
        for a in alphabet:
            t = trans[s][a]
            if t not in reachable:
                reachable.add(t)
                q.append(t)

    states = [s for s in states if s in reachable]
    accept = accept.intersection(reachable)

    # index states and create table marked[i][j] (i > j)
    index = {s: i for i, s in enumerate(states)}
    n = len(states)
    marked = [[False] * n for _ in range(n)]

    def pair(i, j):
        if i == j:
            return None
        return (i, j) if i > j else (j, i)

    # initial marking: final vs non-final 
    for i in range(n):
        for j in range(i):
            si, sj = states[i], states[j]
            if (si in accept) != (sj in accept):
                marked[i][j] = True
                steps.append({
                    "action": "initial_mark",
                    "pair": (si, sj),
                    "reason": "one accepting, one non-accepting",
                    "dependent_on": []
                })

    # iteratively mark additional distinguishable pairs 
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(i):
                if marked[i][j]:
                    continue

                si, sj = states[i], states[j]

                for a in alphabet:
                    ti = trans[si][a]
                    tj = trans[sj][a]

                    pi_pj = pair(index[ti], index[tj])
                    if pi_pj is None:   # same state, no info
                        continue

                    pi, pj = pi_pj
                    if marked[pi][pj]:
                        marked[i][j] = True
                        changed = True
                        steps.append({
                            "action": "propagate_mark",
                            "pair": (si, sj),
                            "symbol": a,
                            "to_pair": (ti, tj),
                            "reason": "transitions lead to already-distinguishable pair",
                            "dependent_on": [(ti, tj)]
                        })
                        break  # stop checking more symbols for this pair

    # build equivalence classes from unmarked pairs
    rep = {s: s for s in states}

    for i in range(n):
        for j in range(i):
            if not marked[i][j]:
                si, sj = states[i], states[j]
                ri, rj = rep[si], rep[sj]
                for k in states:
                    if rep[k] == rj:
                        rep[k] = ri

    groups = defaultdict(list)
    for s in states:
        groups[rep[s]].append(s)

    equiv_classes = list(groups.values())
    steps.append({
        "action": "merge_classes",
        "reason": "formed equivalence classes from unmarked pairs",
        "classes": [sorted(g) for g in equiv_classes],
        "dependent_on": []
    })

    # build minimized DFA 
    new_states = []
    class_name = {}

    for group in equiv_classes:
        name = "[" + ",".join(sorted(group)) + "]"
        new_states.append(name)
        for s in group:
            class_name[s] = name

    new_start = class_name[start]
    new_accept = sorted({class_name[s] for s in accept})

    new_transitions = {ns: {} for ns in new_states}
    for group in equiv_classes:
        rep_state = group[0]
        ns = class_name[rep_state]
        for a in alphabet:
            t = trans[rep_state][a]
            nt = class_name[t]
            new_transitions[ns][a] = nt

    minimized_dfa = {
        "states": new_states,
        "alphabet": alphabet,
        "start_state": new_start,
        "accept_states": new_accept,
        "transitions": new_transitions
    }

    return {
        "minimized_dfa": minimized_dfa,
        "steps": steps,
        "equivalence_classes": equiv_classes
    }
