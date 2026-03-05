from geopy.distance import geodesic


def is_near_gate(lat, lon, gates_df):
    """
    Check if a coordinate is inside a toll gate radius.
    """
    for _, gate in gates_df.iterrows():
        dist = geodesic(
            (lat, lon),
            (gate["lat"], gate["lon"])
        ).meters

        if dist <= gate["radius_m"]:
            return True, gate["name"]

    return False, None


def route_tolls(route_nodes, G, gates_df, toll_price=4.0):
    """
    Detect toll gates crossed and return TOTAL toll cost (AED).
    """

    crossed = set()

    for node in route_nodes:
        lat = G.nodes[node]["y"]
        lon = G.nodes[node]["x"]

        hit, gate = is_near_gate(lat, lon, gates_df)

        if hit:
            crossed.add(gate)

    # compute monetary toll cost
    total_cost = len(crossed) * toll_price

    return float(total_cost)