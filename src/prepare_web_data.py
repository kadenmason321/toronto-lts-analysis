"""
prepare_web_data.py
Exports lean, simplified, standalone GeoJSON files for every city and
layer, saved into web/data/ -- these get fetched at RUNTIME by the
JavaScript map instead of being embedded into one giant HTML file.

Usage:
    python3 src/prepare_web_data.py
"""

import os
import geopandas as gpd
from shapely import set_precision

CITIES = {
    "toronto": "Toronto",
    "vancouver": "Vancouver",
    "corvallis": "Corvallis",
    "seattle": "Seattle",
    "amsterdam": "Amsterdam",
    "new_york_city": "New York City",
}

OUT_DIR = "web/data"


def clean_name(val):
    if val is None:
        return "Unnamed street"
    if isinstance(val, (list, tuple)):
        return str(val[0]) if len(val) > 0 else "Unnamed street"
    return str(val)


def clean_str(val):
    if val is None:
        return "unknown"
    if isinstance(val, (list, tuple)):
        return str(val[0]) if len(val) > 0 else "unknown"
    return str(val)


def prep_geometry(gdf, tolerance=0.0003, precision=0.00002):
    gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)
    gdf["geometry"] = gdf["geometry"].apply(lambda geom: set_precision(geom, grid_size=precision))
    return gdf


def export_lts_layer(city_key, city_label):
    in_path = f"output/{city_key}_lts_scored.geojson"
    if not os.path.exists(in_path):
        print(f"  Skipping {city_label} LTS (file not found: {in_path})")
        return

    gdf = gpd.read_file(in_path)
    gdf = gdf[["geometry", "lts_score", "name", "highway", "facility_type"]].copy()
    gdf["name"] = gdf["name"].apply(clean_name)
    gdf["lts_score"] = gdf["lts_score"].astype(int)
    gdf["highway"] = gdf["highway"].apply(clean_str)
    gdf["facility_type"] = gdf["facility_type"].apply(clean_str)
    gdf = prep_geometry(gdf)

    out_path = f"{OUT_DIR}/{city_key}_lts.geojson"
    gdf.to_file(out_path, driver="GeoJSON")
    size_kb = os.path.getsize(out_path) / 1024
    print(f"  {city_label} LTS: {len(gdf)} segments -> {out_path} ({size_kb:.0f} KB)")


def export_fragments_layer(city_key, city_label):
    in_path = f"output/{city_key}_components.geojson"
    if not os.path.exists(in_path):
        print(f"  Skipping {city_label} fragments (file not found: {in_path})")
        return

    gdf = gpd.read_file(in_path)
    gdf = gdf[gdf["component"].isin(range(10))]
    gdf = gdf[["geometry", "component", "name", "highway"]].copy()
    gdf["name"] = gdf["name"].apply(clean_name)
    gdf["component"] = gdf["component"].astype(int)
    gdf["highway"] = gdf["highway"].apply(clean_str)
    gdf = prep_geometry(gdf)

    out_path = f"{OUT_DIR}/{city_key}_fragments.geojson"
    gdf.to_file(out_path, driver="GeoJSON")
    size_kb = os.path.getsize(out_path) / 1024
    print(f"  {city_label} fragments: {len(gdf)} segments -> {out_path} ({size_kb:.0f} KB)")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Exporting web-ready data to {OUT_DIR}/\n")

    for city_key, city_label in CITIES.items():
        print(f"{city_label}:")
        export_lts_layer(city_key, city_label)
        export_fragments_layer(city_key, city_label)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
