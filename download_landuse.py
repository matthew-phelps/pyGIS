import requests
import osm2geojson
import json
import os

# Define the function to process an area
def process_area(area_id, area_name, polygon_type):
    # Check if the polygon_type is in the form "key=value"
    if "=" in polygon_type:
        print ("found =")
        polygon_key, polygon_value = polygon_type.split("=")
        output_file_path = os.path.join("data", "data_raw", f"{area_name}_{polygon_key}_{polygon_value}.geojson")
        overpass_query = f"""
        [out:xml][timeout:100];
        area({area_id}) -> .area_0;
        (
            way["{polygon_key}"="{polygon_value}"](area.area_0);
            relation["{polygon_key}"="{polygon_value}"](area.area_0);
        );
        (._;>;);
        out body;
        """
        tag_key = polygon_key
    else:
        print ("no =")
        polygon_key = polygon_type
        output_file_path = os.path.join("data", "data_raw", f"{area_name}_{polygon_key}.geojson")
        overpass_query = f"""
        [out:xml][timeout:100];
        area({area_id}) -> .area_0;
        (
            way["{polygon_key}"](area.area_0);
            relation["{polygon_key}"](area.area_0);
        );
        (._;>;);
        out body;
        """
        tag_key = polygon_key

    # Send the request to the Overpass API
    response = requests.post("http://overpass-api.de/api/interpreter", data=overpass_query)

    # Check if the response was successful
    if response.status_code == 200:
        # Get the XML response content as a string
        xml_data = response.content.decode('utf-8')

        # Convert the XML to GeoJSON using osm2geojson
        geojson_data = osm2geojson.xml2geojson(xml_data)

        # Filter the GeoJSON to include only polygons and multipolygons and include only the user-defined property
        filtered_features = []
        for feature in geojson_data['features']:
            if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']:
                # Extract the nested tags structure
                tags = feature['properties'].get('tags', {})
                property_value = tags.get(tag_key, None)

                # Create a new properties dictionary with only the user-defined property
                new_properties = {}
                if property_value:
                    new_properties[tag_key] = property_value

                # Update feature properties with the new properties dictionary
                feature['properties'] = new_properties
                filtered_features.append(feature)

        filtered_geojson_data = {
            "type": "FeatureCollection",
            "features": filtered_features
        }

        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # Save the filtered GeoJSON data to the output file
        with open(output_file_path, "w", encoding="utf-8") as file:
            json.dump(filtered_geojson_data, file, ensure_ascii=False, indent=4)

        print(f"Converted XML to GeoJSON, filtered to polygons, and saved to {output_file_path}")
    else:
        print(f"Error: Overpass API request failed with status code {response.status_code} for area {area_id}")

