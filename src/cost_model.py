def generalized_cost(time_min, toll_cost, value_of_time):
    """
    Economic travel cost model.

    Parameters
    ----------
    time_min : float
    toll_cost : float
    value_of_time : float  (AED per minute)

    Returns
    -------
    float
        Total generalized cost
    """
    return (time_min * value_of_time) + toll_cost


def compute_cost_breakdown(time_min, toll_cost, value_of_time):
    """
    Detailed cost breakdown.
    """
    time_cost = time_min * value_of_time
    total = time_cost + toll_cost

    return {
        "time_cost": time_cost,
        "toll_cost": toll_cost,
        "total_cost": total
    }


def switching_vot(routeA, routeB):
    """
    Solve V where:
    V*tA + cA = V*tB + cB
    """

    tA, cA = routeA["time"], routeA["toll"]
    tB, cB = routeB["time"], routeB["toll"]

    if tA == tB:
        return None

    return (cB - cA) / (tA - tB)