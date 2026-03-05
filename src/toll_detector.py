from geopy.distance import geodesic


def is_near_gate(lat, lon, gates_df):
    """
    Determine whether a coordinate lies within the radius of a toll gate.

    Returns
    -------
    tuple
        (True, gate_name) if inside a gate radius, otherwise (False, None)
    """

    for _, gate in gates_df.iterrows():
        distance = geodesic(
            (lat, lon),
            (gate["lat"], gate["lon"])
        ).meters

        if distance <= gate["radius_m"]:
            return True, gate["name"]

    return False, None


def route_tolls(route_nodes, G, gates_df, toll_price=4.0):
    """
    Calculate the total toll cost for a route.

    Parameters
    ----------
    route_nodes : list
        Ordered list of node IDs representing the route.

    G : networkx graph
        Road network graph.

    gates_df : pandas DataFrame
        Toll gate locations and radii.

    toll_price : float
        Price per toll gate crossing (AED).

    Returns
    -------
    float
        Total toll cost for the route.
    """

    crossed_gates = set()

    for node in route_nodes:
        lat = G.nodes[node]["y"]
        lon = G.nodes[node]["x"]

        hit, gate_name = is_near_gate(lat, lon, gates_df)

        if hit:
            crossed_gates.add(gate_name)

    total_cost = len(crossed_gates) * toll_price

    return float(total_cost)
