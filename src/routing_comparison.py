"""
routing_comparison.py
Compares shortest-path routing on the full Toronto network vs. the
low-stress-only (LTS 1-2) subgraph, for a set of real origin-destination
trips. Reports the detour cost (or impossibility) of staying low-stress.

Usage:
    python3 src/routing_comparison.py config/toronto.yaml
"""

import sys
import yaml
import osmnx as ox
import networkx as nx

# Real trip pairs to test: (label, origin lat/lon, destination lat/lon)
# Add your own here -- pick places you actually know.
TRIPS = [
    ("High Park to Union Station", (43.6465, -79.4637), (43.6453, -79.3806)),
    ("Danforth/Broadview to Union Station", (43.6772, -79.3583), (43.6453, -79.3806)),
    ("Bloor/Shaw to Union Station", (43.6636, -79.4194), (43.6453, -79.3806)),
]


def compare_route(G_full, G_low, origin, destination, label):
    orig_node_full = ox.distance.nearest_nodes(G_full, origin[1], origin[0])
    dest_node_full = ox.distance.nearest_nodes(G_full, destination[1], destination[0])

    orig_node_low = ox.distance.nearest_nodes(G_low, origin[1], origin[0])
    dest_node_low = ox.distance.nearest_nodes(G_low, destination[1], destination[0])

    print(f"\n=== {label} ===")

    try:
        full_path = nx.shortest_path(G_full, orig_node_full, dest_node_full, weight="length")
        full_length = nx.shortest_path_length(G_full, orig_node_full, dest_node_full, weight="length")
        print(f"Full network route: {full_length/1000:.2f} km")
    except nx.NetworkXNoPath:
        print("Full network route: NO PATH FOUND (unexpected)")
        full_length = None

    try:
        low_path = nx.shortest_path(G_low, orig_node_low, dest_node_low, weight="length")
        low_length = nx.shortest_path_length(G_low, orig_node_low, dest_node_low, weight="length")
        print(f"Low-stress-only route: {low_length/1000:.2f} km")

        if full_length:
            detour_pct = 100 * (low_length - full_length) / full_length
            print(f"Detour cost: {detour_pct:+.1f}% longer than direct route")
    except nx.NetworkXNoPath:
        print("Low-stress-only route: NO PATH FOUND -- this trip is impossible "
              "while staying entirely on LTS 1-2 streets")


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    city_name = cfg["city_name"].lower().replace(" ", "_")

    print(f"Loading scored graphs for {city_name}...")
    G_full = ox.load_graphml(f"data/{city_name}_scored_full.graphml")
    G_low = ox.load_graphml(f"data/{city_name}_scored_lowstress.graphml")

    # GraphML round-trip sometimes stores numeric attrs as strings --
    # make sure edge length is numeric for shortest-path weighting
    for G in (G_full, G_low):
        for u, v, key, data in G.edges(keys=True, data=True):
            if "length" in data:
                data["length"] = float(data["length"])

    for label, origin, destination in TRIPS:
        compare_route(G_full, G_low, origin, destination, label)


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
