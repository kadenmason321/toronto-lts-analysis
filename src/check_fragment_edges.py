"""
check_fragment_edges.py
Diagnostic: of the "high-stress" edges (LTS 3-4) that exist WITHIN the
largest low-stress component's neighborhood (i.e. edges connecting two
nodes that are each individually part of some low-stress fragment, but
the edge between them isn't low-stress) -- how many relied on a
DEFAULT speed value vs. a real tagged speed? High reliance on defaults
would suggest fragmentation is partly a data-quality artifact, not a
purely real urban-structure finding.
"""

import sys
import yaml
import osmnx as ox
from score_network import get_speed_kmh, get_lanes, get_facility_type, get_has_parking, get_is_oneway, _first, _numeric_list
from lts_rules import score_segment


def get_speed_kmh_with_flag(row, cfg):
    """Same as get_speed_kmh but also returns whether a default was used."""
    speeds = _numeric_list(row.get("maxspeed"))
    if speeds:
        raw = max(speeds)
        if cfg["speed_unit"] == "mph":
            return raw * 1.60934, False
        return raw, False
    hw = _first(row.get("highway"))
    defaults = cfg["defaults"]["speed_by_highway"]
    return defaults.get(hw, 40), True


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    city_name = cfg["city_name"].lower().replace(" ", "_")

    G = ox.load_graphml(f"data/{city_name}_network.graphml")
    exclude = set(cfg["tags"]["exclude_highways"])

    total_high_stress = 0
    high_stress_used_default = 0

    for u, v, key, data in G.edges(keys=True, data=True):
        hw = _first(data.get("highway"))
        if hw in exclude:
            continue

        speed_kmh, was_default = get_speed_kmh_with_flag(data, cfg)
        lanes = get_lanes(data, cfg)
        facility_type = get_facility_type(data, cfg)
        has_parking = get_has_parking(data, cfg)
        is_oneway = get_is_oneway(data)

        score = score_segment(facility_type, speed_kmh, lanes, has_parking, is_oneway)

        if score >= 3:
            total_high_stress += 1
            if was_default:
                high_stress_used_default += 1

    pct = 100 * high_stress_used_default / total_high_stress if total_high_stress else 0
    print(f"Total high-stress (LTS 3-4) edges: {total_high_stress}")
    print(f"Of those, edges relying on a DEFAULT speed (no real tag): {high_stress_used_default} ({pct:.1f}%)")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
