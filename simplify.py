import json
import logging
from geojson import Feature, FeatureCollection, LineString, dump
from shapely.geometry import LineString as ShapelyLineString, MultiLineString
from shapely.ops import linemerge, unary_union

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def read_geojson(input_file):
    logging.info(f'Reading data from {input_file}')
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['features'], data.get('crs')

def simplify_geometries(features):
    logging.info('Simplifying geometries')
    lines = [ShapelyLineString(feature['geometry']['coordinates']) for feature in features]
    merged = linemerge(unary_union(lines))
    
    if isinstance(merged, ShapelyLineString):
        merged = [merged]
    elif isinstance(merged, MultiLineString):
        merged = merged.geoms
    
    simplified_features = [Feature(geometry=LineString(line.coords), properties={}) for line in merged]
    logging.debug(f'Simplified {len(features)} features into {len(simplified_features)} features')
    return simplified_features

def write_geojson(features, output_file, crs):
    logging.info(f'Writing data to {output_file}')
    feature_collection = FeatureCollection(features)
    if crs:
        feature_collection['crs'] = crs
    with open(output_file, 'w', encoding='utf-8') as f:
        dump(feature_collection, f, ensure_ascii=False, indent=4)
    logging.info(f'Data saved to {output_file} with {len(features)} features')

def process_osm_line_data(input_files, output_files):
    for line_type, input_file in input_files.items():
        features, crs = read_geojson(input_file)
        simplified_features = simplify_geometries(features)
        output_file = output_files.get(line_type)
        if output_file:
            write_geojson(simplified_features, output_file, crs)

