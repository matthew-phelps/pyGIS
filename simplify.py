import json
import os
from shapely.geometry import shape, mapping, Polygon, MultiPolygon, LineString, MultiLineString

def simplify_geometry(geometry, tolerance):
    """
    Simplify the geometry with the given tolerance.
    """
    if isinstance(geometry, (Polygon, MultiPolygon, LineString, MultiLineString)):
        return geometry.simplify(tolerance, preserve_topology=True)
    return geometry

def simplify_features(features, tolerance):
    """
    Simplify the features with the given tolerance.
    """
    simplified_features = []
    for feature in features:
        geom = shape(feature['geometry'])
        simplified_geom = simplify_geometry(geom, tolerance)
        feature['geometry'] = mapping(simplified_geom)
        simplified_features.append(feature)
    return simplified_features

def process_file(input_file, output_file, tolerance):
    # Read the input GeoJSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Ensure the CRS is EPSG:25832
    crs = {
        "type": "name",
        "properties": {
            "name": "EPSG:25832"
        }
    }

    if 'crs' in data:
        print(f"Input CRS for {input_file}: {data['crs']}")
    else:
        print(f"No CRS found in input {input_file}, assuming EPSG:25832.")

    # Simplify the features
    simplified_features = simplify_features(data['features'], tolerance)
    
    # Prepare the simplified GeoJSON data
    simplified_geojson = {
        "type": "FeatureCollection",
        "features": simplified_features,
        "crs": crs
    }
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save the simplified GeoJSON to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(simplified_geojson, f)
    
    print(f"Simplified GeoJSON saved to {output_file}")

def main(file_pairs, tolerance):
    for input_file, output_file in file_pairs:
        process_file(input_file, output_file, tolerance)

if __name__ == "__main__":
    # Define the input and output file paths and the simplification tolerance
    file_pairs = [
        ("data/data_raw/border.geojson", "data/data_raw/border_simplified.geojson"),
        ("data/data_raw/motorways.geojson", "data/data_raw/motorways_simplified.geojson"),
        ("data/data_raw/railways.geojson", "data/data_raw/railways_simplified.geojson")
        # Add more file pairs as needed
    ]
    tolerance = 0.01
    
    # Run the main function
    main(file_pairs, tolerance)
