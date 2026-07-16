"""
test_oneway_effect.py
Diagnostic: how much does the one-way lane-doubling rule contribute to
low-stress network fragmentation? Re-scores WITHOUT doubling and
compares connected-component structure.
"""

import sys
import yaml
import osmnx as ox
import networkx as nx
from score_network import get_speed_kmh, get_lanes, get_facility_type, get_has_parking, get_is_oneway, _first


def score_segment_no_doubling(facility_type, speed_kmh, lanes, has_parking, is_oneway):
    """Same logic as lts_rules.score_segment but WITHOUT the one-way
    lane-doubling, to isolate its effect."""
    effective_lanes = lanes  # no doubling

    if facility_type == "protected":
        return 1
    if facility_type == "bike_lane":
        if has_parking:
            if speed_kmh <= 40 and effective_lanes <= 2: return 2
            elif speed_kmh <= 50 and effective_lanes <= 4: return 3
            else: return 4
        else:
            if speed_kmh <= 30 and effective_lanes <= 2: return 1
            elif speed_kmh <= 40 and effective_lanes <= 2: return 2
            elif speed_kmh <= 50 and effective_lanes <= 4: return 3
            else: return 4
    if speed_kmh <= 30 and effective_lanes <= 2: return 1
    elif speed_kmh <= 40 and effective_lanes <= 2: return 2
    elif speed_kmh <= 50 and effective_lanes <= 4: return 3
    else: return 4


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    city_name = cfg["city_name"].lower().replace(" ", "_")

    G = ox.load_graphml(f"data/{city_name}_network.graphml")
    exclude = set(cfg["tags"]["exclude_highways"])

    edges_to_remove = []
    oneway_count = 0
    oneway_rescued_count = 0

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

        if is_oneway:
            oneway_count += 1

        score_no_doubling = score_segment_no_doubling(
            facility_type, speed_kmh, lanes, has_parking, is_oneway)
        G.edges[u, v, key]["lts_score"] = score_no_doubling

        if is_oneway and score_no_doubling <= 2:
            oneway_rescued_count += 1

    for u, v, key in edges_to_remove:
        G.remove_edge(u, v, key)

    print(f"Total one-way edges in network: {oneway_count}")
    print(f"One-way edges that would score LTS 1-2 WITHOUT doubling: {oneway_rescued_count}")

    G_low = G.edge_subgraph(
        [(u, v, key) for u, v, key, d in G.edges(keys=True, data=True) if d.get("lts_score", 99) <= 2]
    ).copy()
    G_low_undirected = G_low.to_undirected()
    components = list(nx.connected_components(G_low_undirected))
    components.sort(key=len, reverse=True)

    print(f"\nWITHOUT one-way doubling:")
    print(f"Low-stress network: {len(components)} components")
    print(f"Largest component: {len(components[0])} nodes "
          f"({100*len(components[0])/len(G_low_undirected.nodes):.1f}% of low-stress nodes)")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
