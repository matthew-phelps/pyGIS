import geopandas as gpd
from shapely.geometry import shape
import json

def buffer_and_dissolve(input_geojson, buffer_distance, output_geojson):
    """
    Adds a buffer to polygons in a GeoJSON file or GeoDataFrame and dissolves overlapping polygons.
    
    Parameters:
    input_geojson (str or geopandas.GeoDataFrame): Path to the input GeoJSON file or GeoDataFrame.
    buffer_distance (float): Buffer distance in meters.
    output_geojson (str): Path to the output GeoJSON file.
    """
    # If input_geojson is a string (file path), load GeoJSON file into a GeoDataFrame
    if isinstance(input_geojson, str):
        layer_A = gpd.read_file(input_geojson)
    elif isinstance(input_geojson, gpd.GeoDataFrame):
        layer_A = input_geojson
    else:
        raise TypeError("input_geojson should be either a file path (str) or a GeoDataFrame (geopandas.GeoDataFrame)")

    # Ensure the CRS is in meters (assumes EPSG:25832 based on the example)
    layer_A = layer_A.to_crs(epsg=25832)

    # Add a buffer to each polygon
    layer_A['geometry'] = layer_A['geometry'].buffer(buffer_distance)

    # Dissolve overlapping polygons into a single polygon
    dissolved_layer_A = layer_A.dissolve()

    # Save the resulting GeoDataFrame to a new GeoJSON file
    dissolved_layer_A.to_file(output_geojson, driver='GeoJSON')

# Example usage
if __name__ == "__main__":
    input_geojson = 'path_to_your_input_geojson_file.geojson'
    buffer_distance = 100  # Replace with your desired buffer distance in meters
    output_geojson = 'path_to_your_output_geojson_file.geojson'
    
    buffer_and_dissolve(input_geojson, buffer_distance, output_geojson)
