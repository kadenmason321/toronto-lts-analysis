"""
sensitivity_analysis.py
Re-scores the same network multiple times with different LTS-1 speed
thresholds, to see how sensitive the output distribution is to that
one boundary. Answers: "why 30 km/h and not 25 or 35?"

Usage:
    python3 src/sensitivity_analysis.py config/toronto.yaml
"""

import sys
import yaml
import osmnx as ox
import pandas as pd
from lts_rules import score_segment

# Re-use the same tag-reading helpers from score_network.py so we're not
# duplicating logic -- import them directly.
from score_network import (
    get_speed_kmh, get_lanes, get_facility_type, get_has_parking,
    get_is_oneway, _first
)


def score_with_threshold(edges, cfg, lts1_speed):
    """Score every edge using a specific LTS-1 speed threshold, return
    the distribution as a dict."""
    scores = []
    for _, row in edges.iterrows():
        speed_kmh = get_speed_kmh(row, cfg)
        lanes = get_lanes(row, cfg)
        facility_type = get_facility_type(row, cfg)
        has_parking = get_has_parking(row, cfg)
        is_oneway = get_is_oneway(row)
        score = score_segment(facility_type, speed_kmh, lanes, has_parking,
                               is_oneway, lts1_speed=lts1_speed)
        scores.append(score)
    return pd.Series(scores).value_counts().sort_index()


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    city_name = cfg["city_name"].lower().replace(" ", "_")
    graphml_path = f"data/{city_name}_network.graphml"

    print(f"Loading {graphml_path}")
    G = ox.load_graphml(graphml_path)
    edges = ox.graph_to_gdfs(G, nodes=False)

    exclude = set(cfg["tags"]["exclude_highways"])
    edges = edges[~edges["highway"].apply(lambda h: _first(h) in exclude)]
    total = len(edges)

    # Test a range of LTS-1 speed thresholds around the default of 30 km/h
    variants = [20, 25, 30, 35, 40]

    results = {}
    for threshold in variants:
        print(f"Scoring with LTS-1 threshold = {threshold} km/h...")
        results[threshold] = score_with_threshold(edges, cfg, threshold)

    print("\n=== Sensitivity Analysis Results ===")
    print(f"Total edges: {total}\n")
    table = pd.DataFrame(results).fillna(0).astype(int)
    table.index.name = "LTS score"
    table.columns.name = "LTS-1 threshold (km/h)"
    print(table)

    print("\n=== As % of total ===")
    pct_table = (table / total * 100).round(1)
    print(pct_table)


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/toronto.yaml"
    main(config_path)
