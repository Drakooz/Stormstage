"""Role B: where should k trucks wait? Greedy p-median + swap pass, with a move penalty."""
import numpy as np


def expected_cost(sites, demand, T):
    """Expected drive minutes: sum over zones of demand * drive time from nearest site."""
    if len(sites) == 0:
        return np.inf
    return float((demand * T[sites, :].min(axis=0)).sum())


def place_trucks(demand, T, k, current=None, move_penalty_min=3.0, max_rounds=3):
    """Pick k zone indices to stage trucks.

    demand: array (Z,) expected incidents per zone
    T: array (Z, Z) drive minutes between zones
    current: list of k zone indices where trucks are now (None = plan from scratch)
    move_penalty_min: a move must save at least this many expected minutes
    Returns (sites, reasons): sites[i] is truck i's new zone index.
    """
    Z = len(demand)
    reasons = []
    if current is None:
        sites = []
        for _ in range(k):                                   # greedy add
            best = min((s for s in range(Z) if s not in sites),
                       key=lambda s: expected_cost(sites + [s], demand, T))
            sites.append(best)
    else:
        sites = list(current)

    for _ in range(max_rounds):                              # swap pass, one truck at a time
        improved = False
        for i in range(k):
            now_cost = expected_cost(sites, demand, T)
            others = sites[:i] + sites[i + 1:]
            costs = np.array([expected_cost(others + [s], demand, T) for s in range(Z)])
            s_best = int(costs.argmin())
            saving = now_cost - costs[s_best]
            threshold = move_penalty_min if current is not None else 1e-6
            if s_best != sites[i] and saving > threshold:
                reasons.append({"truck": i, "from": sites[i], "to": s_best,
                                "saves_min": round(saving, 1),
                                "demand_to": round(float(demand[s_best]), 2)})
                sites[i] = s_best
                improved = True
        if not improved:
            break
    return sites, reasons
