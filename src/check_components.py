"""
check_components.py
Diagnostic: how fragmented is the low-stress network? Reports overall
connected-component statistics for any city. Optionally checks
specific reference points if provided for that city.
"""

import sys
import yaml
import osmnx as ox
import networkx as nx

# Reference points per city -- add entries here as needed. Cities not
# listed here will just get the overall component stats, no specific
# point checks.
REFERENCE_POINTS = {
    "toronto": [
        ("Union Station", (43.6453, -79.3806)),
        ("High Park", (43.6465, -79.4637)),
        ("Danforth/Broadview", (43.6772, -79.3583)),
        ("Bloor/Shaw", (43.6636, -79.4194)),
    ],
    # Amsterdam reference points: central station and a well-known
    # neighborhood, as a rough analog to the Toronto checks
    "amsterdam": [
        ("Amsterdam Centraal", (52.3791, 4.9003)),
        ("De Pijp", (52.3557, 4.8930)),
        ("Vondelpark area", (52.3579, 4.8686)),
        ("Amsterdam Noord (across the IJ)", (52.3874, 4.9200)),
    ],
}


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    city_name = cfg["city_name"].lower().replace(" ", "_")

    G_low = ox.load_graphml(f"data/{city_name}_scored_lowstress.graphml")
    G_low_undirected = G_low.to_undirected()

    components = list(nx.connected_components(G_low_undirected))
    components.sort(key=len, reverse=True)

    print(f"Low-stress network has {len(components)} separate connected components")
    print(f"Largest component: {len(components[0])} nodes "
          f"({100*len(components[0])/len(G_low_undirected.nodes):.1f}% of all low-stress nodes)")
    print(f"Second largest: {len(components[1]) if len(components) > 1 else 0} nodes\n")

    node_to_component = {}
    for i, comp in enumerate(components):
        for node in comp:
            node_to_component[node] = i

    ref_points = REFERENCE_POINTS.get(city_name)
    if not ref_points:
        print(f"(No reference points configured for '{city_name}' -- skipping point checks)")
        return

    for label, (lat, lon) in ref_points:
        try:
            node = ox.distance.nearest_nodes(G_low, lon, lat)
            comp_idx = node_to_component.get(node)
            comp_size = len(components[comp_idx]) if comp_idx is not None else 0
            in_largest = "YES (main network)" if comp_idx == 0 else f"NO -- isolated island of {comp_size} nodes"
            print(f"{label}: component #{comp_idx}, size {comp_size} -- in largest component? {in_largest}")
        except Exception as e:
            print(f"{label}: could not check ({e})")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
