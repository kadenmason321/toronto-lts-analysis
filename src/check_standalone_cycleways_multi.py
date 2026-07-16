"""
check_standalone_cycleways_multi.py
Runs the same standalone-cycleway diagnostic across small sample areas
in Toronto, Vancouver, Corvallis, and Seattle, to check whether the
Amsterdam finding (protected cycling infra mapped as separate OSM ways,
invisible to a drive-only pull) is unique to Amsterdam or also present
to some degree in the North American cities.
"""

import osmnx as ox

ox.settings.useful_tags_way = ox.settings.useful_tags_way + [
    "cycleway", "cycleway:left", "cycleway:right", "cycleway:both",
]

SAMPLES = {
    "Toronto": "The Beaches, Toronto, Ontario, Canada",
    "Vancouver": "Mount Pleasant, Vancouver, British Columbia, Canada",
    "Corvallis": "Corvallis, Oregon, USA",
    "Seattle": "Capitol Hill, Seattle, Washington, USA",
}


def check_city(city_name, place):
    print(f"\n=== {city_name} ({place}) ===")
    try:
        G_drive = ox.graph_from_place(place, network_type="drive", simplify=True)
        drive_edges = len(G_drive.edges)
    except Exception as e:
        print(f"  Drive pull failed: {e}")
        return

    try:
        G_all = ox.graph_from_place(place, network_type="all", simplify=True)
        all_edges = len(G_all.edges)
    except Exception as e:
        print(f"  All-network pull failed: {e}")
        return

    standalone_cycleways = sum(
        1 for _, _, data in G_all.edges(data=True)
        if data.get("highway") == "cycleway" or
           (isinstance(data.get("highway"), list) and "cycleway" in data.get("highway"))
    )

    print(f"  Drive network: {drive_edges} edges")
    print(f"  All network: {all_edges} edges")
    print(f"  Standalone highway=cycleway ways: {standalone_cycleways}")
    if drive_edges > 0:
        pct = 100 * standalone_cycleways / drive_edges
        print(f"  Standalone cycleways as % of drive network size: {pct:.1f}%")


def main():
    for city_name, place in SAMPLES.items():
        check_city(city_name, place)


if __name__ == "__main__":
    main()
