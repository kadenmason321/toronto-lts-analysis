"""
build_interactive_map.py
Builds a standalone, interactive HTML map with toggleable layers and a
"jump to city" dropdown that pans/zooms the map on selection.

Usage:
    python3 src/build_interactive_map.py

PERFORMANCE NOTES:
- prefer_canvas=True: canvas rendering handles large feature counts
  much better than SVG.
- Geometries are simplified and coordinate-precision-reduced before
  export to cut file size.
- Fragments layers DROP high-stress (component == -1) streets, since
  those are already shown in the corresponding LTS layer -- avoids
  duplicating the same geometry twice per city.
- Each layer's full GeoDataFrame is handed to folium.GeoJson in ONE
  call, never looped per-row in Python.

KNOWN LIMITATION (flagged for next session, not solved tonight):
Even with these optimizations, output/index.html is large (~90MB+)
because Toronto and Amsterdam's LTS + fragments layers each represent
close to their full city network, loaded twice. A more thorough fix
would split this into separate per-city pages rather than one combined
file, or serve data from an external file fetched at runtime instead
of embedding it directly in the HTML. Not implemented tonight --
pushed as-is since it's under GitHub's 100MB hard limit and still
functions, just loads slowly.
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
    -1: "#d9d9d9",
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
    10: "#666666",
}

CITY_JUMP_POINTS = {
    "Toronto": (43.70, -79.42, 11),
    "Vancouver": (49.2827, -123.1207, 12),
    "Corvallis": (44.5646, -123.2620, 13),
    "Seattle": (47.6062, -122.3321, 11),
    "Amsterdam": (52.3676, 4.9041, 12),
}


def clean_name(val):
    if val is None:
        return "Unnamed street"
    if isinstance(val, (list, tuple)):
        return str(val[0]) if len(val) > 0 else "Unnamed street"
    return str(val)


def prep_geometry(gdf):
    gdf["geometry"] = gdf["geometry"].simplify(0.0003, preserve_topology=True)
    gdf["geometry"] = gdf["geometry"].apply(lambda geom: set_precision(geom, grid_size=0.00001))
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
    gdf = gdf[["geometry", "lts_score", "name", "highway", "facility_type"]].copy()
    gdf["name"] = gdf["name"].apply(clean_name)
    gdf["lts_score"] = gdf["lts_score"].astype(int)
    gdf["highway"] = gdf["highway"].astype(str)
    gdf["facility_type"] = gdf["facility_type"].astype(str)
    gdf = prep_geometry(gdf)

    geojson_str = gdf.to_json()
    layer = folium.GeoJson(
        geojson_str,
        name=f"{city_label}: LTS Stress Score",
        style_function=lts_style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "lts_score", "highway", "facility_type"],
            aliases=["Street:", "LTS Score:", "Road type:", "Facility:"],
        ),
    )
    print(f"  Loaded {city_label} LTS layer: {len(gdf)} segments")
    return layer


def load_component_layer(path, city_label):
    if not os.path.exists(path):
        print(f"  Skipping {city_label} fragments (file not found: {path})")
        return None

    gdf = gpd.read_file(path)
    gdf = gdf[gdf["component"] != -1]
    gdf = gdf[["geometry", "component", "name", "highway"]].copy()
    gdf["name"] = gdf["name"].apply(clean_name)
    gdf["component"] = gdf["component"].astype(int)
    gdf["highway"] = gdf["highway"].astype(str)
    gdf = prep_geometry(gdf)

    geojson_str = gdf.to_json()
    layer = folium.GeoJson(
        geojson_str,
        name=f"{city_label}: Low-Stress Network Fragments",
        style_function=component_style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "component", "highway"],
            aliases=["Street:", "Fragment ID:", "Road type:"],
        ),
        show=False,
    )
    print(f"  Loaded {city_label} fragments layer: {len(gdf)} segments")
    return layer


def build_title_html():
    parts = []
    parts.append('<div style="position: fixed; top: 15px; left: 60px; z-index: 1000; ')
    parts.append('background: white; padding: 10px 18px; border-radius: 5px; ')
    parts.append('box-shadow: 0 0 5px rgba(0,0,0,0.3); font-family: sans-serif;">')
    parts.append('<b style="font-size: 16px;">Level of Traffic Stress -- Multi-City Explorer</b><br>')
    parts.append('<span style="font-size: 12px; color: #555;">Use the layer control (top right) to toggle cities and views. Use the dropdown below to jump to a city.</span>')
    parts.append('</div>')
    return "".join(parts)


def build_legend_html():
    parts = []
    parts.append('<div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000; ')
    parts.append('background: white; padding: 10px 15px; border-radius: 5px; ')
    parts.append('box-shadow: 0 0 5px rgba(0,0,0,0.3); font-family: sans-serif; font-size: 12px; max-width: 260px;">')
    parts.append('<b>LTS Stress Score</b><br>')
    parts.append('<span style="color:#1a9850;">&#9632;</span> Low Stress<br>')
    parts.append('<span style="color:#a6d96a;">&#9632;</span> Low-Moderate Stress<br>')
    parts.append('<span style="color:#fc8d59;">&#9632;</span> High Stress<br>')
    parts.append('<span style="color:#d73027;">&#9632;</span> Very High Stress<br>')
    parts.append('<hr style="margin: 6px 0;">')
    parts.append('<b>Low-Stress Network Fragments</b><br>')
    parts.append('<span style="font-size: 11px; color: #555;">Each color = a separate, disconnected low-stress network. High-stress streets are hidden on this layer (see LTS layer for those).</span>')
    parts.append('</div>')
    return "".join(parts)


def build_city_dropdown_html(map_var_name):
    options = ['<option value="">Jump to city...</option>']
    for label, (lat, lon, zoom) in CITY_JUMP_POINTS.items():
        options.append(f'<option value="{lat},{lon},{zoom}">{label}</option>')
    options_html = "".join(options)

    parts = []
    parts.append('<div style="position: fixed; top: 105px; left: 60px; z-index: 1000; ')
    parts.append('background: white; padding: 10px 15px; border-radius: 5px; ')
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

    vancouver_lts = load_lts_layer("output/vancouver_lts_scored.geojson", "Vancouver")
    if vancouver_lts:
        vancouver_lts.add_to(m)

    corvallis_lts = load_lts_layer("output/corvallis_lts_scored.geojson", "Corvallis")
    if corvallis_lts:
        corvallis_lts.add_to(m)

    seattle_lts = load_lts_layer("output/seattle_lts_scored.geojson", "Seattle")
    if seattle_lts:
        seattle_lts.add_to(m)

    amsterdam_lts = load_lts_layer("output/amsterdam_lts_scored.geojson", "Amsterdam")
    if amsterdam_lts:
        amsterdam_lts.add_to(m)

    amsterdam_fragments = load_component_layer("output/amsterdam_components.geojson", "Amsterdam")
    if amsterdam_fragments:
        amsterdam_fragments.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    m.get_root().html.add_child(folium.Element(build_title_html()))
    m.get_root().html.add_child(folium.Element(build_legend_html()))

    map_var_name = m.get_name()
    m.get_root().html.add_child(folium.Element(build_city_dropdown_html(map_var_name)))

    out_path = "output/index.html"
    print(f"Saving to {out_path}...")
    m.save(out_path)
    print(f"Done. Saved interactive map to {out_path}")


if __name__ == "__main__":
    main()
