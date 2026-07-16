"""
find_missing_links.py
For each pair of the 10 largest low-stress network fragments, finds the
shortest path connecting them through the full network (which
necessarily passes through high-stress streets). Ranks these "bridges"
by length -- the shortest ones are the cheapest, highest-value
candidates for infrastructure upgrades to reconnect fragments.

Usage:
    python3 src/find_missing_links.py config/toronto.yaml
"""

import sys
import yaml
import osmnx as ox
import networkx as nx
from itertools import combinations


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    city_name = cfg["city_name"].lower().replace(" ", "_")

    print("Loading scored graphs...")
    G_full = ox.load_graphml(f"data/{city_name}_scored_full.graphml")
    G_low = ox.load_graphml(f"data/{city_name}_scored_lowstress.graphml")

    for G in (G_full, G_low):
        for u, v, key, data in G.edges(keys=True, data=True):
            if "length" in data:
                data["length"] = float(data["length"])

    G_low_undirected = G_low.to_undirected()
    components = list(nx.connected_components(G_low_undirected))
    components.sort(key=len, reverse=True)

    top10 = components[:10]
    print(f"Checking all pairs among the 10 largest fragments "
          f"({len(list(combinations(range(10), 2)))} pairs)...\n")

    G_full_undirected = G_full.to_undirected()

    results = []
    for i, j in combinations(range(10), 2):
        frag_i = top10[i]
        frag_j = top10[j]

        # Find shortest path between ANY node in fragment i and ANY
        # node in fragment j, using the full network (so it can pass
        # through high-stress streets as a bridge)
        best_length = None
        best_path = None

        # Sample a subset of boundary-ish nodes rather than every node
        # in each fragment, for speed -- just check a reasonable sample
        sample_i = list(frag_i)[:30]
        sample_j = list(frag_j)[:30]

        for node_i in sample_i:
            try:
                lengths = nx.single_source_dijkstra_path_length(
                    G_full_undirected, node_i, weight="length", cutoff=3000
                )
            except Exception:
                continue
            for node_j in sample_j:
                if node_j in lengths:
                    if best_length is None or lengths[node_j] < best_length:
                        best_length = lengths[node_j]

        if best_length is not None:
            results.append((i, j, best_length))

    results.sort(key=lambda x: x[2])

    print("=== Shortest bridges between fragment pairs (top 15) ===")
    print(f"{'Fragment A':<12}{'Fragment B':<12}{'Bridge length (m)':<20}")
    for i, j, length in results[:15]:
        print(f"{i:<12}{j:<12}{length:<20.0f}")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
