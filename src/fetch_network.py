"""
fetch_network.py
Pulls a cyclable street network from OpenStreetMap for a given city config,
using OSMnx. Saves the raw graph to data/ as a GraphML file so we don't
have to hit the OSM servers every time we iterate on the scoring logic.

Usage:
    python3 src/fetch_network.py config/toronto.yaml
"""

import sys
import yaml
import osmnx as ox

# By default OSMnx only keeps a whitelist of OSM way tags. cycleway and
# parking tags aren't in that default list, so we add them explicitly —
# otherwise they get silently dropped even though they exist in the source
# OSM data. This is a common gotcha, not a data-quality problem.
ox.settings.useful_tags_way = ox.settings.useful_tags_way + [
    "cycleway",
    "cycleway:left",
    "cycleway:right",
    "cycleway:both",
    "parking:lane:left",
    "parking:lane:right",
    "parking:lane:both",
]

def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    place = cfg["query_place"]
    city_name = cfg["city_name"].lower().replace(" ", "_")

    print(f"Fetching network for: {place}")
    G = ox.graph_from_place(place, network_type="drive", simplify=True)

    out_path = f"data/{city_name}_network.graphml"
    ox.save_graphml(G, out_path)

    print(f"Saved {len(G.nodes)} nodes, {len(G.edges)} edges to {out_path}")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
