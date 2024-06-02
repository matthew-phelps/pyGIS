import requests
import json
from geojson import Feature, FeatureCollection, LineString

# Define the Overpass API endpoint
overpass_url = "http://overpass-api.de/api/interpreter"

# Define the Overpass QL query to get primary, secondary, and tertiary roads in Denmark
overpass_query = """
[out:json][timeout:1800];
area["ISO3166-1"="DK"][admin_level=2]->.a;
(
  way["highway"="motorway"](area.a);
  way["highway"="motorway_link"](area.a);
  way["highway"="trunk"](area.a);
  way["highway"="trunk_link"](area.a);
  way["highway"="primary"](area.a);
  way["highway"="primary_link"](area.a);
  way["highway"="secondary"](area.a);
  way["highway"="secondary_link"](area.a);
  way["highway"="tertiary"](area.a);
);
out body;
>;
out skel qt;
"""

# Send the request to the Overpass API
response = requests.get(overpass_url, params={'data': overpass_query})

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Create a dictionary to store nodes
    nodes = {}
    for element in data['elements']:
        if element['type'] == 'node':
            nodes[element['id']] = (element['lon'], element['lat'])

    # Create GeoJSON features for ways
    features = []
    for element in data['elements']:
        if element['type'] == 'way':
            coordinates = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
            if coordinates:
                geometry = LineString(coordinates)
                feature = Feature(geometry=geometry, properties={'highway': element.get('tags', {}).get('highway')})
                features.append(feature)

    # Create a FeatureCollection
    feature_collection = FeatureCollection(features)

    # Save the GeoJSON to a file
    output_file = 'raw_data/denmark_roads.geojson'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(feature_collection, f, ensure_ascii=False, indent=4)

    print(f"Data downloaded and saved to {output_file}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)