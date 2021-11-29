import geopandas as gpd
from pydantic import BaseModel
from shapely.geometry import Polygon


class Status(BaseModel):
    message: str


def create_shapefile(coordinates, name):
    coord = []
    for coordinate in coordinates:
        coord.append([coordinate['lng'], coordinate['lat']])
    coord.append([coordinates[0]['lng'], coordinates[0]['lat']])

    """ Create    a    polygon    from coordinates"""
    polygon = Polygon(coord)
    gdf = gpd.GeoDataFrame(crs={'init': 'epsg:4326'})
    gdf.loc[0, 'name'] = name
    gdf.loc[0, 'geometry'] = polygon
    gdf.to_file("polygon.shp")
    return gdf
