import json
import os
from collections import defaultdict
from geojson import Feature, FeatureCollection, LineString, MultiPolygon, dump
from pyproj import Transformer

def initialize_transformer(target_epsg):
    return Transformer.from_crs("EPSG:4326", f"EPSG:{target_epsg}", always_xy=True)

def load_geojson(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def reproject_coords(coords, transformer):
    return [transformer.transform(lon, lat) for lon, lat in coords]

def process_features(data, property_key=None, feature_mapping=None, link_mapping=None):
    if link_mapping is None:
        link_mapping = {}
    if feature_mapping is None:
        feature_mapping = {}
        
    features_by_type = defaultdict(list)
    if not feature_mapping:
        # If feature_mapping is empty, process all features together
        features_by_type['all'] = data['features']
    else:
        for feature in data['features']:
            feature_type = feature['properties'].get(property_key)
            if feature_type in link_mapping:
                parent_type = link_mapping[feature_type]
                features_by_type[parent_type].append(feature)
            elif feature_type in feature_mapping:
                features_by_type[feature_type].append(feature)
    
    return features_by_type

def reproject_features(features_by_type, transformer):
    reprojected_data = {}
    for feature_type, features in features_by_type.items():
        reprojected_features = []
        for feature in features:
            geometry = feature['geometry']
            if geometry['type'] == 'LineString':
                reprojected_coords = reproject_coords(geometry['coordinates'], transformer)
                new_geometry = LineString(reprojected_coords)
            elif geometry['type'] == 'MultiPolygon':
                reprojected_polygons = []
                for polygon in geometry['coordinates']:
                    reprojected_polygon = [reproject_coords(ring, transformer) for ring in polygon]
                    reprojected_polygons.append(reprojected_polygon)
                new_geometry = MultiPolygon(reprojected_polygons)
            else:
                continue  # Skip geometries that are not LineString or MultiPolygon

            reprojected_feature = Feature(geometry=new_geometry, properties=feature['properties'])
            reprojected_features.append(reprojected_feature)
        reprojected_data[feature_type] = reprojected_features
        print(f"Reprojected {len(reprojected_features)} features for type {feature_type}")  # Debug: Print reprojected features count
    return reprojected_data

def save_features(reprojected_data, output_path, target_epsg):
    for feature_type, features in reprojected_data.items():
        feature_collection = FeatureCollection(features)

        # Add CRS information to the GeoJSON
        feature_collection['crs'] = {
            "type": "name",
            "properties": {
                "name": f"urn:ogc:def:crs:EPSG::{target_epsg}"
            }
        }

        output_file = output_path.get(feature_type, output_path.get('default'))
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure the directory exists
            with open(output_file, 'w', encoding='utf-8') as f:
                dump(feature_collection, f, ensure_ascii=False, indent=4)
            print(f"Data for {feature_type} saved to {output_file} with {len(features)} features")
        else:
            print(f"No output file specified for feature type: {feature_type}")

def reproject_and_separate(input_file, target_epsg, property_key=None, feature_mapping=None, link_mapping=None, output_directory="data/data_processed", default_output_file=None):
    if link_mapping is None:
        link_mapping = {}
    if feature_mapping is None:
        feature_mapping = {}
    
    if not feature_mapping:
        output_path = {'default': os.path.join(output_directory, default_output_file)}
    else:
        output_path = {key: os.path.join(output_directory, value) for key, value in feature_mapping.items()}
    
    print("Output paths:", output_path)  # Debug: Print output paths
    
    transformer = initialize_transformer(target_epsg)
    data = load_geojson(input_file)
    features_by_type = process_features(data, property_key, feature_mapping, link_mapping)
    
    # Debug: Print feature counts
    for feature_type, features in features_by_type.items():
        print(f"Feature type: {feature_type}, count: {len(features)}")
    
    reprojected_data = reproject_features(features_by_type, transformer)
    return reprojected_data, output_path
