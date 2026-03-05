import osmnx as ox
import networkx as nx
from itertools import islice
import random


# ---------------------------------------------------
# BASIC ROUTING
# ---------------------------------------------------

def shortest_route(G, origin_node, destination_node, weight="length"):
    return ox.shortest_path(G, origin_node, destination_node, weight=weight)


# ---------------------------------------------------
# MULTI ROUTE GENERATION (FAST + CACHED)
# ---------------------------------------------------

# module-level cache so we don't rebuild the simple graph repeatedly
_SIMPLE_GRAPH_CACHE = {}  # key: (id(G), weight_key) -> DiGraph


def _convert_to_simple_graph(G, weight_key):
    """
    Convert OSMnx MultiDiGraph -> DiGraph, keeping the lowest-weight edge
    between each (u,v). Cached for speed.
    """
    cache_key = (id(G), weight_key)
    if cache_key in _SIMPLE_GRAPH_CACHE:
        return _SIMPLE_GRAPH_CACHE[cache_key]

    G_simple = nx.DiGraph()

    # MultiDiGraph may have parallel edges; choose lowest weight
    for u, v, data in G.edges(data=True):
        w = data.get(weight_key, None)
        if w is None:
            # fall back if missing weight
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
    Generate up to k alternative simple paths using chosen weight.
    IMPORTANT: use islice so we do NOT materialize the entire generator.
    """
    G_simple = _convert_to_simple_graph(G, weight)

    gen = nx.shortest_simple_paths(G_simple, origin, destination, weight=weight)
    return list(islice(gen, k))


# ---------------------------------------------------
# ROUTE METRICS
# ---------------------------------------------------

def route_distance(G, route):
    """Return distance in KM"""
    gdf = ox.routing.route_to_gdf(G, route)
    meters = gdf["length"].sum()
    return meters / 1000


def route_travel_time(G, route):
    """Return travel time in MINUTES (requires edge attr travel_time in seconds)"""
    gdf = ox.routing.route_to_gdf(G, route)
    if "travel_time" not in gdf.columns:
        raise ValueError("Edges do not have 'travel_time'. Run ox.add_edge_speeds and ox.add_edge_travel_times first.")
    seconds = gdf["travel_time"].sum()
    return seconds / 60


# ---------------------------------------------------
# SYNTHETIC TRAFFIC
# ---------------------------------------------------

def apply_synthetic_travel_time(G, scenario="road_class"):
    """
    Modify travel_time so routes differ meaningfully.
    Assumes travel_time exists (seconds). Returns G (mutated).
    """
    # Works for MultiDiGraph
    for u, v, k, data in G.edges(keys=True, data=True):
        base_time = data.get("travel_time", None)
        if base_time is None:
            continue

        if scenario == "uniform":
            factor = 1.2

        elif scenario == "road_class":
            highway = str(data.get("highway", ""))

            # ⭐ STRONG MOTORWAY ADVANTAGE NEAR TOLLS
            if "motorway" in highway:
                if data.get("near_toll", False):
                    factor = 0.35   # VERY FAST toll corridors
                else:
                    factor = 0.65   # normal motorway

            elif "primary" in highway:
                factor = 0.95

            elif "secondary" in highway:
                factor = 1.25

            else:
                factor = 2.6   # slow local streets

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

    # IMPORTANT: travel_time changed → invalidate cached simple graphs
    _SIMPLE_GRAPH_CACHE.clear()

    return G


# ---------------------------------------------------
# MULTI-STRATEGY ROUTE SET
# ---------------------------------------------------

def generate_candidate_routes(G, origin, destination, k_each=8, stochastic_runs=6):
    """
    Generate economically diverse routes:
    - fastest (travel_time)
    - shortest (length)
    - toll-avoid proxy
    - balanced toll usage (NEW)
    """

    # -----------------------------
    # FASTEST ROUTES
    # -----------------------------
    fast_routes = k_routes(
        G, origin, destination,
        k=k_each,
        weight="travel_time"
    )

    # -----------------------------
    # SHORTEST DISTANCE
    # -----------------------------
    short_routes = k_routes(
        G, origin, destination,
        k=k_each,
        weight="length"
    )

    # -----------------------------
    # STRONG TOLL AVOID
    # -----------------------------
    G_penalty = G.copy()

    for u, v, kk, data in G_penalty.edges(keys=True, data=True):
        tt = data.get("travel_time", 1)

        # VERY strong avoidance
        if data.get("near_toll", False):
            data["penalty_time"] = tt * 8.0
        else:
            data["penalty_time"] = tt * 1.1

    cheap_routes = k_routes(
        G_penalty,
        origin,
        destination,
        k=k_each,
        weight="penalty_time"
    )

    # -----------------------------
    # ⭐ BALANCED TOLL STRATEGY (NEW)
    # mild penalty → partial toll usage
    # -----------------------------
    G_balanced = G.copy()

    for u, v, kk, data in G_balanced.edges(keys=True, data=True):
        tt = data.get("travel_time", 1)
        if data.get("near_toll", False):
            data["balanced_time"] = tt * 1.8
        else:
            data["balanced_time"] = tt

    balanced_routes = k_routes(
        G_balanced,
        origin,
        destination,
        k=k_each,
        weight="balanced_time"
    )

    # -----------------------------
    # ⭐ STOCHASTIC DIVERSIFICATION (NEW)
    # creates slightly different driver behaviors
    # -----------------------------
    stochastic_routes = []

    for _ in range(stochastic_runs):
        G_stochastic = G.copy()

        # randomize perceived costs
        time_noise = random.uniform(0.9, 1.2)
        toll_penalty = random.uniform(1.2, 3.5)

        for u, v, kk, data in G_stochastic.edges(keys=True, data=True):
            tt = data.get("travel_time", 1)

            # drivers perceive time differently
            perceived_time = tt * time_noise

            # some drivers hate tolls more than others
            if data.get("near_toll", False):
                perceived_time *= toll_penalty

            data["stochastic_time"] = perceived_time

        stochastic_routes += k_routes(
            G_stochastic,
            origin,
            destination,
            k=max(2, k_each // 2),
            weight="stochastic_time"
        )

    # -----------------------------
    # MERGE + REMOVE DUPLICATES
    # -----------------------------
    all_routes = (
        fast_routes
        + short_routes
        + cheap_routes
        + balanced_routes
        + stochastic_routes
    )

    unique = []
    seen = set()

    for r in all_routes:
        t = tuple(r)
        if t not in seen:
            seen.add(t)
            unique.append(r)

    return unique