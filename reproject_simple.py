import geopandas as gpd
from pyproj import CRS

def reproject_geojson(input_geojson, target_crs):
    """
    Reprojects a GeoJSON file to a target CRS and returns the reprojected GeoDataFrame.
    
    Parameters:
    input_geojson (str): Path to the input GeoJSON file.
    target_crs (str or dict or pyproj.CRS): Target CRS specification.
    
    Returns:
    gdf_reprojected (geopandas.GeoDataFrame): Reprojected GeoDataFrame.
    """
    # Load the GeoJSON file into a GeoDataFrame
    gdf = gpd.read_file(input_geojson)

    # Check current CRS and reproject if necessary
    if gdf.crs is None:
        gdf.crs = CRS.from_epsg(4326)  # Assuming input is WGS 84 if CRS is not defined
    if gdf.crs != target_crs:
        gdf_reprojected = gdf.to_crs(target_crs)
    else:
        gdf_reprojected = gdf

    return gdf_reprojected
