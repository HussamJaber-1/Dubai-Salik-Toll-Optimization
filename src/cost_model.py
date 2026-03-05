def generalized_cost(time_min, toll_cost, value_of_time):
    """
    Compute generalized travel cost.

    Generalized cost converts travel time into monetary value
    using the driver's Value of Time (VOT).

    Parameters
    ----------
    time_min : float
        Travel time in minutes.

    toll_cost : float
        Monetary toll cost (AED).

    value_of_time : float
        Driver's value of time in AED per minute.

    Returns
    -------
    float
        Total generalized travel cost.
    """
    return (time_min * value_of_time) + toll_cost


def compute_cost_breakdown(time_min, toll_cost, value_of_time):
    """
    Return a detailed breakdown of generalized cost components.
    """

    time_cost = time_min * value_of_time
    total_cost = time_cost + toll_cost

    return {
        "time_cost": time_cost,
        "toll_cost": toll_cost,
        "total_cost": total_cost
    }


def switching_vot(route_a, route_b):
    """
    Compute the Value of Time (VOT) at which two routes become equally optimal.

    The switching point occurs where:

        V * tA + cA = V * tB + cB

    which solves to:

        V = (cB - cA) / (tA - tB)

    Parameters
    ----------
    route_a : dict
        Dictionary containing route metrics ("time", "toll").

    route_b : dict
        Dictionary containing route metrics ("time", "toll").

    Returns
    -------
    float or None
        Switching value-of-time threshold. Returns None if travel
        times are identical.
    """

    tA, cA = route_a["time"], route_a["toll"]
    tB, cB = route_b["time"], route_b["toll"]

    if tA == tB:
        return None

    return (cB - cA) / (tA - tB)
