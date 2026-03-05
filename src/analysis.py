import numpy as np


def classify_tradeoff(routes_data):
    """
    Classify the toll structure of a route set.

    Parameters
    ----------
    routes_data : list of dict
        Each dictionary must contain:
        {"time": float, "toll": float}

    Returns
    -------
    str
        One of:
        - "no_tradeoff": all routes have the same toll cost
        - "binary": two toll levels (typical avoid vs toll case)
        - "multi_toll": multiple toll levels enabling marginal trade-offs
    """

    unique_tolls = sorted(set(route["toll"] for route in routes_data))

    if len(unique_tolls) <= 1:
        return "no_tradeoff"

    if len(unique_tolls) == 2:
        return "binary"

    return "multi_toll"


def compute_efficiency(route_a, route_b):
    """
    Compute the efficiency of paying additional tolls.

    Efficiency is measured as minutes saved per AED.

    Parameters
    ----------
    route_a : dict
    route_b : dict

    Returns
    -------
    float or None
        Minutes saved per AED. Returns None if toll cost does not increase.
    """

    delta_time = route_a["time"] - route_b["time"]
    delta_toll = route_b["toll"] - route_a["toll"]

    if delta_toll <= 0:
        return None

    return delta_time / delta_toll


def simulate_lifestyle_choice(routes_data, vot):
    """
    Select the economically optimal route for a given Value of Time.

    Parameters
    ----------
    routes_data : list of dict
    vot : float
        Value of time (AED per minute)

    Returns
    -------
    dict
        Route with the lowest generalized cost.
    """

    from src.cost_model import generalized_cost

    best_route = min(
        routes_data,
        key=lambda r: generalized_cost(r["time"], r["toll"], vot)
    )

    return best_route


def lifestyle_distribution(routes_data, vot_values):
    """
    Simulate route choices across a range of Value-of-Time levels.

    Parameters
    ----------
    routes_data : list of dict
    vot_values : iterable

    Returns
    -------
    list
        Index of the chosen route for each VOT value.
    """

    chosen_indices = []

    for vot in vot_values:
        best_route = simulate_lifestyle_choice(routes_data, vot)
        route_index = routes_data.index(best_route)
        chosen_indices.append(route_index)

    return chosen_indices
