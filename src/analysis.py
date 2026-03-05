import numpy as np


def classify_tradeoff(routes_data):
    """
    Determine if trip has meaningful non-binary toll tradeoff.

    routes_data = list of dicts with keys:
        time, toll
    """

    unique_tolls = sorted(set(r["toll"] for r in routes_data))

    if len(unique_tolls) <= 1:
        return "no_tradeoff"

    if len(unique_tolls) == 2:
        return "binary"

    return "multi_toll"


def compute_efficiency(routeA, routeB):
    """
    Minutes saved per AED between two routes.
    """

    delta_time = routeA["time"] - routeB["time"]
    delta_toll = routeB["toll"] - routeA["toll"]

    if delta_toll <= 0:
        return None

    return delta_time / delta_toll


def simulate_lifestyle_choice(routes_data, vot):
    """
    Choose optimal route for a given lifestyle VoT.
    """

    from src.cost_model import generalized_cost

    best = min(
        routes_data,
        key=lambda r: generalized_cost(r["time"], r["toll"], vot)
    )

    return best


def lifestyle_distribution(routes_data, vot_values):
    """
    Simulate which routes are chosen across VoT spectrum.
    """

    chosen_indices = []

    for v in vot_values:
        best = simulate_lifestyle_choice(routes_data, v)
        idx = routes_data.index(best)
        chosen_indices.append(idx)

    return chosen_indices