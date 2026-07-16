"""
check_node_snapping.py
Diagnostic: near the Dundas St W / Humber River area (where a visual
"touch" between two different-colored fragments was observed on the
mobile map), check whether there are pairs of nodes that are
extremely close together geographically (a few meters) but belong to
DIFFERENT connected components -- which would indicate an unsnapped
node pair from the standalone-cycleway merge, rather than a genuine
disconnection.
"""

import sys
import yaml
import osmnx as ox
import networkx as nx
from itertools import combinations

CENTER_LAT = 43.6503
CENTER_LON = -79.5067
RADIUS_METERS = 500


def haversine_m(lat1, lon1, lat2, lon2):
    import math
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2*R*math.asin(math.sqrt(a))


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    city_name = cfg["city_name"].lower().replace(" ", "_")

    print("Loading graphs...")
    G_low = ox.load_graphml(f"data/{city_name}_scored_lowstress.graphml")
    G_low_undirected = G_low.to_undirected()

    components = list(nx.connected_components(G_low_undirected))
    components.sort(key=len, reverse=True)
    node_to_component = {}
    for i, comp in enumerate(components):
        for node in comp:
            node_to_component[node] = i

    nearby_nodes = []
    for node, data in G_low.nodes(data=True):
        lat, lon = data.get("y"), data.get("x")
        if lat is None or lon is None:
            continue
        dist = haversine_m(CENTER_LAT, CENTER_LON, float(lat), float(lon))
        if dist <= RADIUS_METERS:
            nearby_nodes.append((node, float(lat), float(lon)))

    print(f"Found {len(nearby_nodes)} low-stress-network nodes within "
          f"{RADIUS_METERS}m of the observed touch point")

    print("\nChecking all pairs for near-miss disconnections...")
    found_issue = False
    checked = 0
    for (n1, lat1, lon1), (n2, lat2, lon2) in combinations(nearby_nodes, 2):
        checked += 1
        dist = haversine_m(lat1, lon1, lat2, lon2)
        if dist < 10:
            comp1 = node_to_component.get(n1)
            comp2 = node_to_component.get(n2)
            if comp1 != comp2:
                found_issue = True
                print(f"  FOUND: nodes {n1} and {n2} are {dist:.1f}m apart "
                      f"but in DIFFERENT components ({comp1} vs {comp2})")
                print(f"    Node {n1}: ({lat1}, {lon1})")
                print(f"    Node {n2}: ({lat2}, {lon2})")

    print(f"\nChecked {checked} node pairs.")
    if not found_issue:
        print("No near-miss unsnapped nodes found in this area. The visual "
              "'touch' was likely just a coincidence of screen resolution/"
              "zoom level, not an actual graph anomaly -- the fragments are "
              "genuinely disconnected as shown, just geographically close.")
    else:
        print("CONFIRMED: found unsnapped near-miss node pair(s) -- this "
              "supports the node-snapping-failure theory from the merge "
              "process.")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
