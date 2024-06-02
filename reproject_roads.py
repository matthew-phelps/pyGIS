import json
import os
from collections import defaultdict
from geojson import Feature, FeatureCollection, LineString, dump
from pyproj import Transformer

# Define the input and output files
input_file = 'data/data_raw/denmark_roads.geojson'
target_epsg = '25832'
feature_mapping = {
    'motorway': 'motorways.geojson',
    'trunk': 'trunks.geojson',
    'primary': 'primary.geojson',
    'secondary': 'secondary.geojson',
    'tertiary': 'tertiary.geojson'
}

# Map link types to their parent types
link_mapping = {
    'motorway_link': 'motorway',
    'trunk_link': 'trunk',
    'primary_link': 'primary',
    'secondary_link': 'secondary',
    'tertiary_link': 'tertiary'
}

output_path = {key: os.path.join("data/data_processed", value) for key, value in feature_mapping.items()}
# Initialize the transformer to convert from WGS84 (EPSG:4326) to UTM zone 32N (EPSG:25832)
transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{target_epsg}", always_xy=True)

# Read the input GeoJSON file
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create a dictionary to hold the features for each feature type
features_by_type = defaultdict(list)



# Function to reproject coordinates
def reproject_coords(coords):
    return [transformer.transform(lon, lat) for lon, lat in coords]

# Separate features based on feature type, grouping link types with their parents and reproject coordinates
for feature in data['features']:
    feature_type = feature['properties'].get('highway')
    if feature_type in link_mapping:
        parent_type = link_mapping[feature_type]
        features_by_type[parent_type].append(feature)
    elif feature_type in feature_type:
        features_by_type[feature_type].append(feature)

# Reproject coordinates and write each feature type to a separate GeoJSON file
for feature_type, features in features_by_type.items():
    reprojected_features = []
    for feature in features:
        geometry = feature['geometry']
        if geometry['type'] == 'LineString':
            reprojected_coords = reproject_coords(geometry['coordinates'])
            new_geometry = LineString(reprojected_coords)
            reprojected_feature = Feature(geometry=new_geometry, properties=feature['properties'])
            reprojected_features.append(reprojected_feature)
    feature_collection = FeatureCollection(reprojected_features)
    
    # Add CRS information to the GeoJSON
    feature_collection['crs'] = {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:EPSG::25832"
        }
    }
    
    output_path = feature_mapping.get(feature_type)
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            dump(feature_collection, f, ensure_ascii=False, indent=4)
        print(f"Data for {feature_type} saved to {output_path} with {len(reprojected_features)} features")

print("All feature data processed and saved.")
