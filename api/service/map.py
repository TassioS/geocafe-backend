import os
from datetime import datetime

from pyproj import Proj
from rasterstats import zonal_stats
from shapely.geometry import shape

from api.service.utils import create_shapefile


def retrieve_dates():
    dates = []
    directory = r'images/'
    for filename in os.listdir(directory):
        if filename.startswith("STA_NDVI_"):
            date = filename.removeprefix('STA_NDVI_').removesuffix('.tif')
            dates.append(datetime.strptime(date, "%d_%m_%Y"))
    dates.sort(reverse=True)
    return dates


def calculate_area(coordinates):
    coord = []
    for coordinate in coordinates:
        coord.append([coordinate['lng'], coordinate['lat']])
    coord.append([coordinates[0]['lng'], coordinates[0]['lat']])
    co = {"type": "Polygon", "coordinates": [coord]}
    lon, lat = zip(*co['coordinates'][0])
    pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")
    x, y = pa(lon, lat)
    cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
    return shape(cop).area


def calculate_stats_from_area(coordinates, name, date):
    create_shapefile(coordinates, name)
    stats = zonal_stats('polygon.shp', f'images/STA_NDVI_{date}.tif')
    return {
        'mean': stats[0]['mean'],
        'min': stats[0]['min'],
        'max': stats[0]['max']
    }
