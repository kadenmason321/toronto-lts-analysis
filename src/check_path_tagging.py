"""
check_path_tagging.py
Diagnostic: checks whether highway=path (+ bicycle=designated) is a
common tagging pattern for cycling infrastructure -- a pattern our
current pipeline does NOT treat as a standalone cycleway (only
highway=cycleway is merged in), so this would be a real, uncaught
blind spot similar to the original Amsterdam finding.

Uses a bounding box directly (rather than a place name) since several
NYC neighborhood names aren't cleanly polygon-bounded in Nominatim.
Box covers the Hudson River Greenway area near Chelsea/Hell's Kitchen.
"""

import osmnx as ox

ox.settings.useful_tags_way = ox.settings.useful_tags_way + [
    "bicycle", "foot", "cycleway",
]

# (west, south, east, north) -- small box along the Hudson River
# Greenway, roughly W 30th St to W 23rd St, Manhattan
BBOX = (-74.010, 40.744, -73.995, 40.756)

print("Pulling full network for Hudson River Greenway area (bbox)...")
G_all = ox.graph_from_bbox(bbox=BBOX, network_type="all", simplify=True)
print(f"Total edges: {len(G_all.edges)}")

path_count = 0
path_with_bicycle_designated = 0
cycleway_count = 0

for _, _, data in G_all.edges(data=True):
    hw = data.get("highway")
    is_path = hw == "path" or (isinstance(hw, list) and "path" in hw)
    is_cycleway = hw == "cycleway" or (isinstance(hw, list) and "cycleway" in hw)

    if is_cycleway:
        cycleway_count += 1
    if is_path:
        path_count += 1
        bike = data.get("bicycle")
        if bike == "designated" or (isinstance(bike, list) and "designated" in bike):
            path_with_bicycle_designated += 1

print(f"\nhighway=cycleway ways: {cycleway_count} (currently merged in)")
print(f"highway=path ways (total): {path_count}")
print(f"highway=path + bicycle=designated: {path_with_bicycle_designated} "
      f"(NOT currently merged in -- potential blind spot)")

if path_with_bicycle_designated > 0:
    print("\nCONFIRMED: highway=path + bicycle=designated is a real pattern "
          "here, invisible to the pipeline just like standalone cycleways "
          "were before tonight's fix.")
else:
    print("\nNo instances found in this bbox.")
