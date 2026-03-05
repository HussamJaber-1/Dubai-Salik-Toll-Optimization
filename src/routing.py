import osmnx as ox
import networkx as nx
from itertools import islice
import random


# Cache used to avoid rebuilding simplified graphs repeatedly
_SIMPLE_GRAPH_CACHE = {}


def shortest_route(G, origin_node, destination_node, weight="length"):
    """
    Compute the shortest path between two nodes using a specified edge weight.
    """
    return ox.shortest_path(G, origin_node, destination_node, weight=weight)


def _convert_to_simple_graph(G, weight_key):
    """
    Convert an OSMnx MultiDiGraph to a simple directed graph.

    Parallel edges are collapsed by keeping the edge with the lowest
    value for the selected weight attribute. The result is cached so
    repeated routing operations remain fast.
    """
    cache_key = (id(G), weight_key)

    if cache_key in _SIMPLE_GRAPH_CACHE:
        return _SIMPLE_GRAPH_CACHE[cache_key]

    G_simple = nx.DiGraph()

    for u, v, data in G.edges(data=True):
        w = data.get(weight_key)
        if w is None:
            w = data.get("length", 1)

        if G_simple.has_edge(u, v):
            if w < G_simple[u][v].get(weight_key, float("inf")):
                G_simple[u][v][weight_key] = w
        else:
            G_simple.add_edge(u, v, **{weight_key: w})

    _SIMPLE_GRAPH_CACHE[cache_key] = G_simple
    return G_simple


def k_routes(G, origin, destination, k=3, weight="length"):
    """
    Generate up to k alternative simple routes between origin and destination.
    """
    G_simple = _convert_to_simple_graph(G, weight)

    path_generator = nx.shortest_simple_paths(G_simple, origin, destination, weight=weight)

    return list(islice(path_generator, k))


def route_distance(G, route):
    """
    Compute total route distance in kilometers.
    """
    gdf = ox.routing.route_to_gdf(G, route)
    meters = gdf["length"].sum()
    return meters / 1000


def route_travel_time(G, route):
    """
    Compute total route travel time in minutes.

    Requires edges to contain a 'travel_time' attribute.
    """
    gdf = ox.routing.route_to_gdf(G, route)

    if "travel_time" not in gdf.columns:
        raise ValueError(
            "Edges must contain 'travel_time'. Run ox.add_edge_speeds() "
            "and ox.add_edge_travel_times() first."
        )

    seconds = gdf["travel_time"].sum()
    return seconds / 60


def apply_synthetic_travel_time(G, scenario="road_class"):
    """
    Modify edge travel times to simulate different traffic conditions.
    """
    for u, v, k, data in G.edges(keys=True, data=True):

        base_time = data.get("travel_time")
        if base_time is None:
            continue

        if scenario == "uniform":
            factor = 1.2

        elif scenario == "road_class":
            highway = str(data.get("highway", ""))

            if "motorway" in highway:
                factor = 0.35 if data.get("near_toll", False) else 0.65
            elif "primary" in highway:
                factor = 0.95
            elif "secondary" in highway:
                factor = 1.25
            else:
                factor = 2.6

        elif scenario == "peak_like":
            lanes = data.get("lanes", 1)

            try:
                lanes = float(lanes)
            except Exception:
                lanes = 1

            factor = max(0.8, 2.5 / lanes)

        else:
            factor = 1.0

        noise = random.uniform(0.9, 1.3)

        data["travel_time"] = base_time * factor * noise

    # Invalidate cached routing graphs since travel times changed
    _SIMPLE_GRAPH_CACHE.clear()

    return G


def generate_candidate_routes(G, origin, destination, k_each=8, stochastic_runs=6):
    """
    Generate a diverse set of candidate routes between origin and destination.

    Routes are generated using multiple routing strategies:
        - fastest routes (travel time)
        - shortest routes (distance)
        - strong toll avoidance
        - balanced toll usage
        - stochastic variations representing different driver preferences
    """

    # Fastest routes
    fast_routes = k_routes(G, origin, destination, k=k_each, weight="travel_time")

    # Shortest distance routes
    short_routes = k_routes(G, origin, destination, k=k_each, weight="length")

    # Toll-avoidance strategy
    G_penalty = G.copy()

    for u, v, k, data in G_penalty.edges(keys=True, data=True):
        tt = data.get("travel_time", 1)

        if data.get("near_toll", False):
            data["penalty_time"] = tt * 8.0
        else:
            data["penalty_time"] = tt * 1.1

    cheap_routes = k_routes(G_penalty, origin, destination, k=k_each, weight="penalty_time")

    # Balanced toll usage strategy
    G_balanced = G.copy()

    for u, v, k, data in G_balanced.edges(keys=True, data=True):
        tt = data.get("travel_time", 1)

        if data.get("near_toll", False):
            data["balanced_time"] = tt * 1.8
        else:
            data["balanced_time"] = tt

    balanced_routes = k_routes(G_balanced, origin, destination, k=k_each, weight="balanced_time")

    # Stochastic route diversification
    stochastic_routes = []

    for _ in range(stochastic_runs):

        G_stochastic = G.copy()

        time_noise = random.uniform(0.9, 1.2)
        toll_penalty = random.uniform(1.2, 3.5)

        for u, v, k, data in G_stochastic.edges(keys=True, data=True):

            tt = data.get("travel_time", 1)

            perceived_time = tt * time_noise

            if data.get("near_toll", False):
                perceived_time *= toll_penalty

            data["stochastic_time"] = perceived_time

        stochastic_routes += k_routes(
            G_stochastic,
            origin,
            destination,
            k=max(2, k_each // 2),
            weight="stochastic_time",
        )

    # Merge and remove duplicate routes
    all_routes = (
        fast_routes
        + short_routes
        + cheap_routes
        + balanced_routes
        + stochastic_routes
    )

    unique_routes = []
    seen = set()

    for r in all_routes:
        t = tuple(r)
        if t not in seen:
            seen.add(t)
            unique_routes.append(r)

    return unique_routes
