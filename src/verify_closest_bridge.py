"""
verify_closest_bridge.py
Re-checks a single fragment pair's shortest bridge using ALL nodes
(not a sample), for a trustworthy number on a specific candidate found
by find_missing_links.py.
"""

import sys
import yaml
import osmnx as ox
import networkx as nx

FRAG_A = 0
FRAG_B = 9


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    city_name = cfg["city_name"].lower().replace(" ", "_")

    G_full = ox.load_graphml(f"data/{city_name}_scored_full.graphml")
    G_low = ox.load_graphml(f"data/{city_name}_scored_lowstress.graphml")

    for u, v, key, data in G_full.edges(keys=True, data=True):
        if "length" in data:
            data["length"] = float(data["length"])

    G_low_undirected = G_low.to_undirected()
    components = list(nx.connected_components(G_low_undirected))
    components.sort(key=len, reverse=True)

    frag_a = components[FRAG_A]
    frag_b = components[FRAG_B]

    G_full_undirected = G_full.to_undirected()

    best_length = None
    best_pair = None

    print(f"Checking ALL nodes: fragment {FRAG_A} ({len(frag_a)} nodes) "
          f"vs fragment {FRAG_B} ({len(frag_b)} nodes)...")

    for node_a in frag_a:
        lengths = nx.single_source_dijkstra_path_length(
            G_full_undirected, node_a, weight="length", cutoff=3000
        )
        for node_b in frag_b:
            if node_b in lengths:
                if best_length is None or lengths[node_b] < best_length:
                    best_length = lengths[node_b]
                    best_pair = (node_a, node_b)

    print(f"\nTrue shortest bridge: {best_length:.0f} m")
    print(f"Between nodes: {best_pair}")

    node_a_data = G_full.nodes[best_pair[0]]
    node_b_data = G_full.nodes[best_pair[1]]
    print(f"Node A location: {node_a_data['y']}, {node_a_data['x']}")
    print(f"Node B location: {node_b_data['y']}, {node_b_data['x']}")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
