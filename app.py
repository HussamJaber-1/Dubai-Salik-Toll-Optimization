import osmnx as ox
import pandas as pd

from src.routing import generate_candidate_routes, route_travel_time
from src.toll_detector import route_tolls


def load_network(graph_path):
    """Load the road network graph."""
    print("Loading road network...")
    return ox.load_graphml(graph_path)


def load_toll_gates(csv_path):
    """Load Salik toll gate locations."""
    print("Loading toll gate data...")
    return pd.read_csv(csv_path)


def evaluate_routes(G, origin, destination, gates_df):
    """
    Generate and evaluate candidate routes.
    """

    routes = generate_candidate_routes(G, origin, destination)

    results = []

    for route in routes:

        time_min = route_travel_time(G, route)
        toll_cost = route_tolls(route, G, gates_df)

        results.append({
            "time": time_min,
            "toll": toll_cost
        })

    return results


def main():

    graph_path = "data/dubai.graphml"
    gates_path = "data/salik_gates.csv"

    G = load_network(graph_path)
    gates_df = load_toll_gates(gates_path)

    # Example OD nodes (replace with your test nodes if needed)
    nodes = list(G.nodes)
    origin = nodes[100]
    destination = nodes[500]

    results = evaluate_routes(G, origin, destination, gates_df)

    print("Route evaluation results:")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
