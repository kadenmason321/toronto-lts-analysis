"""
connectivity_analysis.py
Builds a low-stress-only subgraph (LTS 1-2 edges) from the scored
network, then compares routing on the full network vs. the low-stress
network for a set of real origin-destination trips. This answers:
"where does forcing a low-stress route cause a detour, or make a trip
impossible?"

Usage:
    python3 src/connectivity_analysis.py config/toronto.yaml
"""

import sys
import yaml
import osmnx as ox
import networkx as nx
from lts_rules import score_segment
from score_network import (
    get_speed_kmh, get_lanes, get_facility_type, get_has_parking,
    get_is_oneway, _first
)


def score_graph(G, cfg):
    """Attach lts_score as an edge attribute directly on the graph,
    so NetworkX routing can use it. Returns the same graph, mutated."""
    exclude = set(cfg["tags"]["exclude_highways"])
    edges_to_remove = []

    for u, v, key, data in G.edges(keys=True, data=True):
        hw = _first(data.get("highway"))
        if hw in exclude:
            edges_to_remove.append((u, v, key))
            continue

        speed_kmh = get_speed_kmh(data, cfg)
        lanes = get_lanes(data, cfg)
        facility_type = get_facility_type(data, cfg)
        has_parking = get_has_parking(data, cfg)
        is_oneway = get_is_oneway(data)

        score = score_segment(facility_type, speed_kmh, lanes, has_parking, is_oneway)
        G.edges[u, v, key]["lts_score"] = score

    for u, v, key in edges_to_remove:
        G.remove_edge(u, v, key)

    return G


def build_low_stress_subgraph(G, max_lts=2):
    """Returns a new graph containing only edges with lts_score <= max_lts."""
    edges_to_keep = [
        (u, v, key) for u, v, key, data in G.edges(keys=True, data=True)
        if data.get("lts_score", 99) <= max_lts
    ]
    G_low = G.edge_subgraph(
        [(u, v, key) for u, v, key in edges_to_keep]
    ).copy()
    return G_low


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    city_name = cfg["city_name"].lower().replace(" ", "_")
    graphml_path = f"data/{city_name}_network.graphml"

    print(f"Loading {graphml_path}")
    G = ox.load_graphml(graphml_path)

    print("Scoring all edges...")
    G = score_graph(G, cfg)
    print(f"Full network: {len(G.nodes)} nodes, {len(G.edges)} edges")

    print("Building low-stress (LTS 1-2) subgraph...")
    G_low = build_low_stress_subgraph(G, max_lts=2)
    print(f"Low-stress network: {len(G_low.nodes)} nodes, {len(G_low.edges)} edges")

    pct_nodes = 100 * len(G_low.nodes) / len(G.nodes)
    pct_edges = 100 * len(G_low.edges) / len(G.edges)
    print(f"\nLow-stress subgraph retains {pct_nodes:.1f}% of nodes, "
          f"{pct_edges:.1f}% of edges")

    # Save both graphs so later scripts (routing) don't need to
    # re-score from scratch every time
    ox.save_graphml(G, f"data/{city_name}_scored_full.graphml")
    ox.save_graphml(G_low, f"data/{city_name}_scored_lowstress.graphml")
    print(f"\nSaved scored graphs to data/{city_name}_scored_full.graphml "
          f"and data/{city_name}_scored_lowstress.graphml")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
