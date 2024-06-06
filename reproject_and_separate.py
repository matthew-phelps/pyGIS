import json
import os
from collections import defaultdict
from geojson import Feature, FeatureCollection, LineString, dump
from pyproj import Transformer

def initialize_transformer(target_epsg):
    return Transformer.from_crs("EPSG:4326", f"EPSG:{target_epsg}", always_xy=True)

def load_geojson(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def reproject_coords(coords, transformer):
    return [transformer.transform(lon, lat) for lon, lat in coords]

def process_features(data, property_key, feature_mapping, link_mapping=None):
    if link_mapping is None:
        link_mapping = {}
        
    features_by_type = defaultdict(list)
    for feature in data['features']:
        feature_type = feature['properties'].get(property_key)
        if feature_type in link_mapping:
            parent_type = link_mapping[feature_type]
            features_by_type[parent_type].append(feature)
        elif feature_type in feature_mapping:
            features_by_type[feature_type].append(feature)
    
    return features_by_type

def reproject_and_save(features_by_type, output_path, transformer, target_epsg):
    for feature_type, features in features_by_type.items():
        reprojected_features = []
        for feature in features:
            geometry = feature['geometry']
            if geometry['type'] == 'LineString':
                reprojected_coords = reproject_coords(geometry['coordinates'], transformer)
                new_geometry = LineString(reprojected_coords)
                reprojected_feature = Feature(geometry=new_geometry, properties=feature['properties'])
                reprojected_features.append(reprojected_feature)
        print(f"Reprojected {len(reprojected_features)} features for type {feature_type}")  # Debug: Print reprojected features count
        feature_collection = FeatureCollection(reprojected_features)

        # Add CRS information to the GeoJSON
        feature_collection['crs'] = {
            "type": "name",
            "properties": {
                "name": f"urn:ogc:def:crs:EPSG::{target_epsg}"
            }
        }

        output_file = output_path.get(feature_type)
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure the directory exists
            with open(output_file, 'w', encoding='utf-8') as f:
                dump(feature_collection, f, ensure_ascii=False, indent=4)
            print(f"Data for {feature_type} saved to {output_file} with {len(reprojected_features)} features")
        else:
            print(f"No output file specified for feature type: {feature_type}")

def reproject_and_separate(input_file, target_epsg, property_key, feature_mapping, link_mapping=None, output_directory="data/data_processed"):
    if link_mapping is None:
        link_mapping = {}
        
    output_path = {key: os.path.join(output_directory, value) for key, value in feature_mapping.items()}
    print("Output paths:", output_path)  # Debug: Print output paths
    
    transformer = initialize_transformer(target_epsg)
    data = load_geojson(input_file)
    features_by_type = process_features(data, property_key, feature_mapping, link_mapping)
    
    # Debug: Print feature counts
    for feature_type, features in features_by_type.items():
        print(f"Feature type: {feature_type}, count: {len(features)}")
    
    reproject_and_save(features_by_type, output_path, transformer, target_epsg)
    print("All feature data processed and saved.")
