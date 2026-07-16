"""
fetch_network.py
Pulls a cyclable street network from OpenStreetMap for a given city
config, using OSMnx. Saves the raw graph to data/ as a GraphML file.

Usage:
    python3 src/fetch_network.py config/toronto.yaml

ARCHITECTURAL NOTE (added after the Amsterdam finding):
By default this pulls network_type="drive" -- the drivable road
network. In North American cities, protected cycle tracks are usually
tagged onto the parent road (cycleway=track), so a drive-only pull
still captures them. In cities like Amsterdam, protected cycling
infrastructure is very often mapped as an entirely SEPARATE OSM way
(highway=cycleway), invisible to a drive-only pull.

If a city's config sets include_standalone_cycleways: true, this
script ALSO pulls network_type="all" and merges in any standalone
highway=cycleway ways that aren't already part of the drive network.
Those merged-in ways get a special marker attribute
(_standalone_cycleway = True) so score_network.py can treat them as
automatically protected, rather than running them through the normal
tag-based facility_type logic (which wouldn't find a cycleway= tag on
them, since the WAY ITSELF is the cycleway).
"""

import sys
import yaml
import osmnx as ox
import networkx as nx

ox.settings.useful_tags_way = ox.settings.useful_tags_way + [
    "cycleway",
    "cycleway:left",
    "cycleway:right",
    "cycleway:both",
    "parking:lane:left",
    "parking:lane:right",
    "parking:lane:both",
]


def merge_standalone_cycleways(G_drive, place):
    """Pulls the full (all-modes) network, finds ways tagged
    highway=cycleway that aren't already in the drive network, and
    merges them in with a _standalone_cycleway marker."""
    print("  Pulling full network to find standalone cycleways...")
    G_all = ox.graph_from_place(place, network_type="all", simplify=True)

    added = 0
    for u, v, key, data in G_all.edges(keys=True, data=True):
        hw = data.get("highway")
        is_cycleway = hw == "cycleway" or (isinstance(hw, list) and "cycleway" in hw)
        if not is_cycleway:
            continue
        if G_drive.has_edge(u, v, key):
            continue  # already present, don't duplicate

        # Make sure the nodes exist in G_drive before adding the edge
        if u not in G_drive:
            G_drive.add_node(u, **G_all.nodes[u])
        if v not in G_drive:
            G_drive.add_node(v, **G_all.nodes[v])

        data = dict(data)
        data["_standalone_cycleway"] = True
        G_drive.add_edge(u, v, key=key, **data)
        added += 1

    print(f"  Merged in {added} standalone cycleway edges")
    return G_drive


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    place = cfg["query_place"]
    city_name = cfg["city_name"].lower().replace(" ", "_")
    include_standalone = cfg.get("include_standalone_cycleways", False)

    print(f"Fetching network for: {place}")
    G = ox.graph_from_place(place, network_type="drive", simplify=True)
    print(f"Drive network: {len(G.nodes)} nodes, {len(G.edges)} edges")

    if include_standalone:
        G = merge_standalone_cycleways(G, place)
        print(f"After merge: {len(G.nodes)} nodes, {len(G.edges)} edges")

    out_path = f"data/{city_name}_network.graphml"
    ox.save_graphml(G, out_path)

    print(f"Saved {len(G.nodes)} nodes, {len(G.edges)} edges to {out_path}")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
