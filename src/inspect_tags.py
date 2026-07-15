"""
inspect_tags.py
Quick diagnostic: how complete is our OSM tag coverage for the attributes
LTS scoring needs? This tells us how much we'll be leaning on defaults.
"""

import sys
import osmnx as ox

def main(graphml_path):
    G = ox.load_graphml(graphml_path)
    edges = ox.convert.graph_to_gdf(G, nodes=False) if hasattr(ox.convert, "graph_to_gdf") else ox.graph_to_gdfs(G, nodes=False)

    total = len(edges)
    print(f"Total edges: {total}\n")

    for col in ["highway", "maxspeed", "lanes", "cycleway", "cycleway:left", "cycleway:right", "oneway"]:
        if col in edges.columns:
            present = edges[col].notna().sum()
            print(f"{col:20s}: {present}/{total} tagged ({100*present/total:.1f}%)")
        else:
            print(f"{col:20s}: NOT PRESENT in this dataset")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/toronto_network.graphml"
    main(path)
