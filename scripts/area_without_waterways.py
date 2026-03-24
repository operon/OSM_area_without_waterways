"""
area_without_waterways.py

Description :
------------
Génère une grille sur une zone OSM et identifie les cellules contenant
ou non des éléments "waterway". Produit une carte HTML interactive (Leaflet).

Version :
--------
v1.1

Auteur:
-------
operon

Licence :
--------
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...

Source du code :
--------
Ce script a été partiellement généré avec l’aide de ChatGPT (OpenAI),
puis adapté et validé manuellement.

Dépendances :
------------
- requests
- shapely >= 2.0
"""

# === Standard library ===
import os
import json
import math

# === Third-party ===
import requests
from shapely.geometry import Point, LineString, box, mapping
from shapely.ops import linemerge, polygonize, unary_union
from shapely.prepared import prep
from shapely.strtree import STRtree


# === PARAMÈTRES ===
relation_id = 3338038
zone_km = 4.4
overlap_ratio = 0.33
zone_josm_km = 4

if not (0 <= overlap_ratio < 1):
    raise ValueError("❌ 'overlap_ratio' doit être compris entre 0 (inclus) et 1 (exclus)")


# === 1. Télécharger le polygone ===
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = f"""
[out:json];
relation({relation_id});
way(r);
(._;>;);
out body;
"""
response = requests.post(
    overpass_url,
    data={"data": overpass_query},
    timeout=240
)
data = response.json()
print(f"✅ Téléchargement polygone OK")


# === 2. Construire le polygone ===
zone_name = "Zone inconnue"
for el in data["elements"]:
    if el["type"] == "relation" and "tags" in el:
        zone_name = el["tags"].get("name", zone_name)
        break

nodes = {el["id"]: (el["lon"], el["lat"]) for el in data["elements"] if el["type"] == "node"}
lines = []
for el in data["elements"]:
    if el["type"] == "way":
        coords = [nodes[node_id] for node_id in el["nodes"] if node_id in nodes]
        if len(coords) >= 2:
            lines.append(LineString(coords))  # ✅ corrigé

merged = linemerge(lines)  # ✅ corrigé
polygons = list(polygonize(merged))  # ✅ corrigé
polygon = unary_union(polygons)  # ✅ corrigé

if polygon.is_empty:
    raise ValueError("❌ Impossible de construire le polygone à partir des données OSM")

centroid = polygon.centroid
print(f"✅ Construction polygone OK")


# === 3. Télécharger les waterways ===
print(f"✅ Début de Téléchargement waterway")
bbox = polygon.bounds
bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"

waterway_query = f"""
[out:json];
(
  way["waterway"]({bbox_str});
);
(._;>;);
out body;
"""
response = requests.post(overpass_url, data={"data": waterway_query})
waterway_data = response.json()

nb_waterways = sum(
    1 for el in waterway_data["elements"]
    if el["type"] == "way" and "tags" in el and "waterway" in el["tags"]
)
print(f"✅ Téléchargement waterway OK - {nb_waterways} waterway(s) trouvés")


# === 4. Extraction noeuds ===
print(f"✅ Début extraction noeuds des waterway ...")
waterway_nodes = []
prepared_polygon = prep(polygon)
nodes_elements = [el for el in waterway_data["elements"] if el["type"] == "node"]

for el in nodes_elements:
    point = Point(el["lon"], el["lat"])  # ✅ corrigé
    if prepared_polygon.contains(point):
        waterway_nodes.append(point)

print(f"✅ Extraction OK - {len(waterway_nodes)} nœud(s)")


# === 4ter. Lignes waterways ===
waterway_nodes_dict = {
    el["id"]: (el["lon"], el["lat"])
    for el in waterway_data["elements"] if el["type"] == "node"
}

waterway_lines = []
for el in waterway_data["elements"]:
    if el["type"] == "way" and "tags" in el and "waterway" in el["tags"]:
        coords = [waterway_nodes_dict.get(nid) for nid in el["nodes"] if nid in waterway_nodes_dict]
        if len(coords) >= 2:
            waterway_lines.append(LineString(coords))  # ✅ corrigé

waterway_lines = [l for l in waterway_lines if isinstance(l, LineString)]  # ✅ corrigé
line_tree = STRtree(waterway_lines)


# === 5. Grille ===
centroid_lat = polygon.centroid.y

grid_size_lat_deg = zone_km / 111
grid_size_lon_deg = zone_km / (111 * math.cos(math.radians(centroid_lat)))

step_lat = grid_size_lat_deg * (1 - overlap_ratio)
step_lon = grid_size_lon_deg * (1 - overlap_ratio)

minx, miny, maxx, maxy = polygon.bounds
tree = STRtree(list(waterway_nodes))

grid_features = []

x = minx
while x < maxx:
    y = miny
    while y < maxy:
        cell = box(x, y, x + grid_size_lon_deg, y + grid_size_lat_deg)  # ✅ corrigé

        if prepared_polygon.intersects(cell):
            indices = tree.query(cell)
            nodes_in_cell = [waterway_nodes[i] for i in indices if cell.covers(waterway_nodes[i])]

            grid_features.append({
                "type": "Feature",
                "geometry": mapping(cell),  # ✅ corrigé
                "properties": {
                    "has_waterway": len(nodes_in_cell) > 0
                }
            })

        y += step_lat
    x += step_lon


# === 6. GeoJSON ===
geojson_output = {
    "type": "FeatureCollection",
    "features": grid_features
}

geojson_str = json.dumps(geojson_output)


# HTML de la carte Leaflet.js
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Carte des cellules</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
    <style>
        #map {{
            width: 100%;
            height: 100vh;
        }}
    </style>
</head>
<body>
<div id="map"></div>

<script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
<script>

    var map = L.map('map').setView([{polygon.centroid.y}, {polygon.centroid.x}], 12);

    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }}).addTo(map);

    var geojsonData = {geojson_str};

    function style(feature) {{
        return {{
            fillColor: feature.properties.has_waterway ? 'blue' : 'lightgray',
            weight: 1,
            color: 'black',
            fillOpacity: 0.3
        }};
    }}

    L.geoJSON(geojsonData, {{
        style: style,
        onEachFeature: function (feature, layer) {{
            var props = feature.properties;
layer.bindPopup(`
    <b>Cellule</b><br>
    Has waterway: ${{props.has_waterway}}<br>
    Node count: ${{props.node_count}}<br>
    <a href="${{props.josm_url}}" target="_blank">🧭 Ouvrir dans JOSM</a>
`);
        }}
    }}).addTo(map);

</script>
</body>
</html>
"""


# === 8. Export corrigé ===
script_dir = os.path.dirname(os.path.abspath(__file__))
export_dir = os.path.join(script_dir, "export")
os.makedirs(export_dir, exist_ok=True)

output_file = os.path.join(export_dir, "carte_grille_leaflet.html")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"✅ Carte HTML créée : {output_file}")
