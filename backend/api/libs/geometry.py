import numpy as np
import pyproj
from shapely.geometry import Polygon

transformer = pyproj.Transformer.from_crs("epsg:3857", "epsg:9779") # 9779 = RGF93 v2 (lon-lat) -> https://epsg.io/9779

def get_area_polygon(in_poly_coords):
    poly_coords = [ transformer.transform(point[0], point[1]) for point in in_poly_coords ]
    geod = pyproj.Geod(ellps="GRS80")
    poly = Polygon(poly_coords)
    return abs(geod.geometry_area_perimeter(poly)[0])

def get_distance(in_line_coords):
    coords = np.array([ transformer.transform(point[0], point[1]) for point in in_line_coords ])
    geod = pyproj.Geod(ellps="GRS80")
    [ coords_lon, coords_lats ] = np.hsplit(coords, 2)
    coords_lon = coords_lon.reshape(1, coords_lon.shape[0])[0]
    coords_lats = coords_lats.reshape(1, coords_lats.shape[0])[0]
    return geod.line_length(coords_lon, coords_lats)