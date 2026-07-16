"""
check_amsterdam_cycleways.py
Diagnostic: does Amsterdam's cycling infrastructure live mostly as
SEPARATE OSM ways (highway=cycleway) rather than as tags on drivable
roads? If so, our drive-only network pull would be systematically
missing most of it -- unlike North American cities where cycle tracks
are usually tagged onto the parent road.
"""

import osmnx as ox

ox.settings.useful_tags_way = ox.settings.useful_tags_way + [
    "cycleway", "cycleway:left", "cycleway:right", "cycleway:both",
]

PLACE = "De Pijp, Amsterdam, Netherlands"  # small, well-known cycling-heavy neighborhood

print("Pulling DRIVE network (what our pipeline currently uses)...")
G_drive = ox.graph_from_place(PLACE, network_type="drive", simplify=True)
print(f"Drive network: {len(G_drive.edges)} edges")

print("\nPulling ALL network (includes separate cycleway/path ways)...")
G_all = ox.graph_from_place(PLACE, network_type="all", simplify=True)
print(f"All network: {len(G_all.edges)} edges")

# Count how many edges in each are explicitly tagged as standalone
# cycleways (highway=cycleway), which the drive network would exclude
# by definition
cycleway_ways_in_all = sum(
    1 for _, _, data in G_all.edges(data=True)
    if data.get("highway") == "cycleway" or
       (isinstance(data.get("highway"), list) and "cycleway" in data.get("highway"))
)

print(f"\nStandalone 'highway=cycleway' ways in the ALL network: {cycleway_ways_in_all}")
print(f"These would be COMPLETELY MISSING from our drive-only pipeline.")
