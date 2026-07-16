"""
export_components.py
Labels every edge in a city's low-stress subgraph with its connected
component ID, then exports to GeoJSON for visualization.

Usage:
    python3 src/export_components.py config/amsterdam.yaml
"""

import sys
import yaml
import osmnx as ox
import networkx as nx
import geopandas as gpd


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    city_name = cfg["city_name"].lower().replace(" ", "_")

    print("Loading scored graphs...")
    G_full = ox.load_graphml(f"data/{city_name}_scored_full.graphml")
    G_low = ox.load_graphml(f"data/{city_name}_scored_lowstress.graphml")

    for u, v, key, data in G_full.edges(keys=True, data=True):
        if "lts_score" in data:
            data["lts_score"] = int(data["lts_score"])

    G_low_undirected = G_low.to_undirected()
    components = list(nx.connected_components(G_low_undirected))
    components.sort(key=len, reverse=True)

    print(f"Found {len(components)} components")

    node_to_component = {}
    for i, comp in enumerate(components):
        rank = i if i < 10 else 10
        for node in comp:
            node_to_component[node] = rank

    for u, v, key, data in G_full.edges(keys=True, data=True):
        if u in node_to_component and v in node_to_component and data.get("lts_score", 99) <= 2:
            data["component"] = node_to_component[u]
        else:
            data["component"] = -1

    edges = ox.graph_to_gdfs(G_full, nodes=False)
    edges = edges.reset_index()[["geometry", "lts_score", "component", "highway", "name"]]

    out_path = f"output/{city_name}_components.geojson"
    edges.to_file(out_path, driver="GeoJSON")
    print(f"Saved {out_path}")

    print("\nComponent size key:")
    for i in range(min(10, len(components))):
        print(f"  Component {i}: {len(components[i])} nodes")
    remaining = len(components) - 10 if len(components) > 10 else 0
    print(f"  Component 10: 'other' -- all remaining {remaining} smaller fragments combined")
    print(f"  Component -1: high-stress streets (not part of low-stress network)")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)


