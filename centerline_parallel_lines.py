import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon
from shapely.ops import unary_union, linemerge
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define input and output paths
input_geojson_path = "motorways.geojson"
output_geojson_path = "centerline_motorways.geojson"
buffer_distance = 10  # Buffer distance in meters
simplify_tolerance = 0.001  # Simplify tolerance in meters

def create_centerline(motorway_gdf, buffer_distance):
    # Ensure geometries are valid
    motorway_gdf = motorway_gdf[motorway_gdf.is_valid]
    logger.info(f"Valid geometries count: {len(motorway_gdf)}")

    # Create a buffer around each line
    buffered = motorway_gdf.buffer(buffer_distance, cap_style=2)
    logger.info(f"Buffered geometries created.")

    # Dissolve the buffers into a single geometry
    dissolved = unary_union(buffered)
    logger.info(f"Geometries dissolved.")

    # Convert dissolved Polygon or MultiPolygon into lines
    lines = []
    if isinstance(dissolved, Polygon):
        lines.append(dissolved.exterior)
    elif isinstance(dissolved, MultiPolygon):
        for polygon in dissolved.geoms:
            lines.append(polygon.exterior)
        dissolved = MultiLineString(lines)
        logger.info(f"Converted MultiPolygon to MultiLineString.")
    else:
        logger.warning(f"Unexpected geometry type after dissolving: {type(dissolved)}")
        raise ValueError(f"Unexpected geometry type after dissolving buffers: {type(dissolved)}")

    # Merge the lines into a single centerline
    if isinstance(dissolved, (MultiLineString, LineString)):
        centerline = linemerge(dissolved)
    else:
        logger.warning(f"Unexpected geometry type after converting: {type(dissolved)}")
        raise ValueError(f"Unexpected geometry type after converting: {type(dissolved)}")

    return centerline

def simplify_centerline(centerline, tolerance):
    # Simplify the centerline
    simplified_centerline = centerline.simplify(tolerance)
    logger.info(f"Centerline simplified.")
    return simplified_centerline

# Load the motorway vector data from GeoJSON
motorway_gdf = gpd.read_file(input_geojson_path)
logger.info(f"Motorway data loaded: {len(motorway_gdf)} features")

# Check CRS and reproject if necessary
if motorway_gdf.crs != "EPSG:25832":
    motorway_gdf = motorway_gdf.to_crs("EPSG:25832")
    logger.info(f"Data reprojected to EPSG:25832")

# Merge the parallel lines into a single centerline
centerline = create_centerline(motorway_gdf, buffer_distance)

# Simplify the centerline
simplified_centerline = simplify_centerline(centerline, simplify_tolerance)

# Create a GeoDataFrame to save the result
centerline_gdf = gpd.GeoDataFrame(geometry=[simplified_centerline], crs=motorway_gdf.crs)

# Save the centerline to a new GeoJSON file
centerline_gdf.to_file(output_geojson_path, driver='GeoJSON')
logger.info(f"Centerline created and saved successfully to {output_geojson_path}")
