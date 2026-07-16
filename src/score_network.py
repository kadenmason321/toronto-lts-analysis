"""
score_network.py
Applies the LTS rule engine to a real OSM street network, using a city
config to translate raw OSM tags into the clean inputs the rule engine
expects.

Usage:
    python3 src/score_network.py config/toronto.yaml
"""

import sys
import yaml
import osmnx as ox
import geopandas as gpd
from lts_rules import score_segment

MPH_TO_KMH = 1.60934


def _first(val):
    if isinstance(val, list):
        return val[0] if val else None
    return val


def _numeric_list(val):
    if val is None:
        return []
    if not isinstance(val, list):
        val = [val]
    nums = []
    for v in val:
        if v is None:
            continue
        try:
            digits = "".join(c for c in str(v) if c.isdigit() or c == ".")
            if digits:
                nums.append(float(digits))
        except ValueError:
            continue
    return nums


def get_speed_kmh(row, cfg):
    speeds = _numeric_list(row.get("maxspeed"))
    if speeds:
        raw = max(speeds)
        if cfg["speed_unit"] == "mph":
            return raw * MPH_TO_KMH
        return raw
    hw = _first(row.get("highway"))
    defaults = cfg["defaults"]["speed_by_highway"]
    return defaults.get(hw, 40)


def get_lanes(row, cfg):
    lanes = _numeric_list(row.get("lanes"))
    if lanes:
        return int(max(lanes))
    hw = _first(row.get("highway"))
    defaults = cfg["defaults"]["lanes_by_highway"]
    return defaults.get(hw, 2)


def is_standalone_cycleway(row):
    """Checks for the _standalone_cycleway marker explicitly, rather
    than relying on Python truthiness -- pandas fills missing values
    in this column with NaN for rows that never had the attribute set,
    and NaN is TRUTHY in Python (bool(float('nan')) == True), which
    would otherwise incorrectly mark every edge as a standalone
    cycleway. GraphML save/load can also turn True into the string
    "True", so check for both forms explicitly."""
    val = row.get("_standalone_cycleway")
    return val is True or val == "True" or val == "true"


def get_facility_type(row, cfg):
    if is_standalone_cycleway(row):
        return "protected"

    tag_keys = cfg["tags"]["cycleway_side_keys"]
    value_map = cfg["tags"]["cycleway_values"]
    for key in tag_keys:
        raw_val = row.get(key)
        raw_val = _first(raw_val)
        if raw_val and raw_val in value_map:
            return value_map[raw_val]
    return "mixed"


def get_has_parking(row, cfg):
    parking_keys = cfg["tags"]["parking_keys"]
    present_values = set(cfg["tags"]["parking_present_values"])
    for key in parking_keys:
        raw_val = _first(row.get(key))
        if raw_val in present_values:
            return True
    return False


def get_is_oneway(row):
    val = row.get("oneway")
    val = _first(val)
    return bool(val) and str(val).lower() in ("true", "yes", "1")


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    city_name = cfg["city_name"].lower().replace(" ", "_")
    graphml_path = f"data/{city_name}_network.graphml"

    print(f"Loading {graphml_path}")
    G = ox.load_graphml(graphml_path)
    edges = ox.graph_to_gdfs(G, nodes=False)

    exclude = set(cfg["tags"]["exclude_highways"])
    before = len(edges)
    edges = edges[~edges["highway"].apply(lambda h: _first(h) in exclude)]
    print(f"Excluded {before - len(edges)} edges (motorways/trunk roads). {len(edges)} remain.")

    scores = []
    facility_types = []
    for _, row in edges.iterrows():
        speed_kmh = get_speed_kmh(row, cfg)
        lanes = get_lanes(row, cfg)
        facility_type = get_facility_type(row, cfg)
        has_parking = get_has_parking(row, cfg)
        is_oneway = get_is_oneway(row)

        score = score_segment(facility_type, speed_kmh, lanes, has_parking, is_oneway)
        scores.append(score)
        facility_types.append(facility_type)

    edges["lts_score"] = scores
    edges["facility_type"] = facility_types

    print("\nLTS score distribution:")
    print(edges["lts_score"].value_counts().sort_index())
    print("\nFacility type distribution:")
    print(edges["facility_type"].value_counts())

    out_path = f"output/{city_name}_lts_scored.geojson"
    edges.reset_index()[["geometry", "lts_score", "facility_type", "highway", "name"]].to_file(out_path, driver="GeoJSON")
    print(f"\nSaved scored network to {out_path}")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
