"""
build_mobile_map.py
A lighter version of the interactive map: Toronto and Amsterdam's LTS
stress score layers, PLUS their fragments/connectivity layers -- but
the fragments layers drop both high-stress streets (component == -1)
AND the "other/minor fragments" bucket (component == 10, which
combines 1000+ tiny scattered fragments), keeping only the 10 largest
NAMED fragments per city. This keeps the actual comparative story
(Toronto fragmented vs. Amsterdam mostly-unified) while cutting the
long tail of visual/data clutter that isn't adding much value anyway.

Usage:
    python3 src/build_mobile_map.py
"""

import os
import geopandas as gpd
import folium
from shapely import set_precision

LTS_COLORS = {
    1: "#1a9850",
    2: "#a6d96a",
    3: "#fc8d59",
    4: "#d73027",
}

COMPONENT_COLORS = {
    0: "#377eb8",
    1: "#e41a1c",
    2: "#4daf4a",
    3: "#984ea3",
    4: "#ff7f00",
    5: "#b8860b",
    6: "#a65628",
    7: "#f781bf",
    8: "#ffd700",
    9: "#66c2a5",
}

CITY_JUMP_POINTS = {
    "Toronto": (43.70, -79.42, 11),
    "Amsterdam": (52.3676, 4.9041, 12),
}


def clean_name(val):
    if val is None:
        return "Unnamed street"
    if isinstance(val, (list, tuple)):
        return str(val[0]) if len(val) > 0 else "Unnamed street"
    return str(val)


def prep_geometry(gdf):
    gdf["geometry"] = gdf["geometry"].simplify(0.0006, preserve_topology=True)
    gdf["geometry"] = gdf["geometry"].apply(lambda geom: set_precision(geom, grid_size=0.00002))
    return gdf


def lts_style_function(feature):
    score = feature["properties"].get("lts_score", 3)
    return {"color": LTS_COLORS.get(score, "#999999"), "weight": 2, "opacity": 0.8}


def component_style_function(feature):
    comp = feature["properties"].get("component", -1)
    return {"color": COMPONENT_COLORS.get(comp, "#999999"), "weight": 2, "opacity": 0.8}


def load_lts_layer(path, city_label):
    if not os.path.exists(path):
        print(f"  Skipping {city_label} (file not found: {path})")
        return None

    gdf = gpd.read_file(path)
    gdf = gdf[["geometry", "lts_score", "name"]].copy()
    gdf["name"] = gdf["name"].apply(clean_name)
    gdf["lts_score"] = gdf["lts_score"].astype(int)
    gdf = prep_geometry(gdf)

    geojson_str = gdf.to_json()
    layer = folium.GeoJson(
        geojson_str,
        name=f"{city_label}: LTS Stress Score",
        style_function=lts_style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "lts_score"],
            aliases=["Street:", "LTS Score:"],
        ),
    )
    print(f"  Loaded {city_label} LTS layer: {len(gdf)} segments")
    return layer


def load_component_layer(path, city_label):
    if not os.path.exists(path):
        print(f"  Skipping {city_label} fragments (file not found: {path})")
        return None

    gdf = gpd.read_file(path)
    gdf = gdf[gdf["component"].isin(range(10))]
    gdf = gdf[["geometry", "component", "name"]].copy()
    gdf["name"] = gdf["name"].apply(clean_name)
    gdf["component"] = gdf["component"].astype(int)
    gdf = prep_geometry(gdf)

    geojson_str = gdf.to_json()
    layer = folium.GeoJson(
        geojson_str,
        name=f"{city_label}: Low-Stress Network Fragments",
        style_function=component_style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "component"],
            aliases=["Street:", "Fragment ID:"],
        ),
        show=False,
    )
    print(f"  Loaded {city_label} fragments layer (top 10 only): {len(gdf)} segments")
    return layer


def build_title_html():
    parts = []
    parts.append('<div style="position: fixed; top: 10px; left: 10px; right: 10px; z-index: 1000; ')
    parts.append('background: white; padding: 8px 12px; border-radius: 5px; ')
    parts.append('box-shadow: 0 0 5px rgba(0,0,0,0.3); font-family: sans-serif;">')
    parts.append('<b style="font-size: 14px;">LTS Explorer (Mobile) -- Toronto vs Amsterdam</b>')
    parts.append('</div>')
    return "".join(parts)


def build_legend_html():
    parts = []
    parts.append('<div style="position: fixed; bottom: 20px; left: 10px; z-index: 1000; ')
    parts.append('background: white; padding: 8px 12px; border-radius: 5px; ')
    parts.append('box-shadow: 0 0 5px rgba(0,0,0,0.3); font-family: sans-serif; font-size: 11px; max-width: 200px;">')
    parts.append('<b>LTS Score</b><br>')
    parts.append('<span style="color:#1a9850;">&#9632;</span> Low Stress<br>')
    parts.append('<span style="color:#a6d96a;">&#9632;</span> Low-Moderate<br>')
    parts.append('<span style="color:#fc8d59;">&#9632;</span> High Stress<br>')
    parts.append('<span style="color:#d73027;">&#9632;</span> Very High<br>')
    parts.append('<hr style="margin: 4px 0;">')
    parts.append('<b>Fragments</b><br>')
    parts.append('<span style="font-size: 10px; color: #555;">Top 10 largest low-stress networks shown per city.</span>')
    parts.append('</div>')
    return "".join(parts)


def build_city_dropdown_html(map_var_name):
    options = ['<option value="">Jump to city...</option>']
    for label, (lat, lon, zoom) in CITY_JUMP_POINTS.items():
        options.append(f'<option value="{lat},{lon},{zoom}">{label}</option>')
    options_html = "".join(options)

    parts = []
    parts.append('<div style="position: fixed; top: 55px; left: 10px; z-index: 1000; ')
    parts.append('background: white; padding: 8px 12px; border-radius: 5px; ')
    parts.append('box-shadow: 0 0 5px rgba(0,0,0,0.3); font-family: sans-serif; font-size: 13px;">')
    parts.append('<select id="cityJumpSelect" onchange="jumpToCity()" ')
    parts.append('style="font-size: 13px; padding: 4px;">')
    parts.append(options_html)
    parts.append('</select>')
    parts.append('</div>')
    parts.append('<script>')
    parts.append('function jumpToCity() {')
    parts.append('  var val = document.getElementById("cityJumpSelect").value;')
    parts.append('  if (!val) { return; }')
    parts.append('  var parts = val.split(",");')
    parts.append(f'  {map_var_name}.setView([parseFloat(parts[0]), parseFloat(parts[1])], parseInt(parts[2]));')
    parts.append('}')
    parts.append('</script>')
    return "".join(parts)


def main():
    m = folium.Map(
        location=[43.70, -79.42],
        zoom_start=11,
        tiles="CartoDB positron",
        prefer_canvas=True,
    )

    print("Loading layers...")

    toronto_lts = load_lts_layer("output/toronto_lts_scored.geojson", "Toronto")
    if toronto_lts:
        toronto_lts.add_to(m)

    toronto_fragments = load_component_layer("output/toronto_components.geojson", "Toronto")
    if toronto_fragments:
        toronto_fragments.add_to(m)

    amsterdam_lts = load_lts_layer("output/amsterdam_lts_scored.geojson", "Amsterdam")
    if amsterdam_lts:
        amsterdam_lts.add_to(m)

    amsterdam_fragments = load_component_layer("output/amsterdam_components.geojson", "Amsterdam")
    if amsterdam_fragments:
        amsterdam_fragments.add_to(m)

    folium.LayerControl(collapsed=True).add_to(m)

    m.get_root().html.add_child(folium.Element(build_title_html()))
    m.get_root().html.add_child(folium.Element(build_legend_html()))

    map_var_name = m.get_name()
    m.get_root().html.add_child(folium.Element(build_city_dropdown_html(map_var_name)))

    out_path = "mobile.html"
    print(f"Saving to {out_path}...")
    m.save(out_path)
    print(f"Done. Saved mobile map to {out_path}")


if __name__ == "__main__":
    main()
