import os
import uuid
from datetime import datetime

import rasterio
import rasterio.features
import rasterio.warp
from rasterio.mask import mask as rast_mask


def crop_image(fields, date):
    # the polygon GeoJSON geometry
    geoms = []
    for field in fields:
        field_coordinate = field['coordinates']
        coord = []
        for coordinate in field_coordinate:
            coord.append([coordinate['lng'], coordinate['lat']])
        coord.append([field_coordinate[0]['lng'], field_coordinate[0]['lat']])
        geoms.append({"type": "Polygon", "coordinates": [coord]})
    # load the raster, mask it by the polygon and crop it
    with rasterio.open(f"images/STA_NDVI_{date}.tif") as src:
        out_image, out_transform = rast_mask(src, geoms, crop=True)
    out_meta = src.meta.copy()

    # save the resulting raster
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})
    filename = str(uuid.uuid4())
    with rasterio.open(f"images/{filename}.tif", "w", **out_meta) as dest:
        dest.write(out_image)
    return f'{filename}.tif'


def getPixelHistory(lon, lat):
    values_history = []
    directory = r'images/'
    for filename in os.listdir(directory):
        if filename.startswith("STA_NDVI_"):
            date = filename.removeprefix('STA_NDVI_').removesuffix('.tif')
            date = datetime.strptime(date, "%d_%m_%Y")
            f_date = date.strftime(
                "%d/%m/%y")
            # open map
            dataset = rasterio.open(f"images/{filename}")
            # get pixel x+y of the coordinate
            py, px = dataset.index(lon, lat)
            # create 1x1px window of the pixel
            window = rasterio.windows.Window(px - 1 // 2, py - 1 // 2, 1, 1)
            # read rgb values of the window
            clip = dataset.read(window=window)
            values_history.append(
                {"f_date": f_date, "date": date, "value": clip[0][0][0]})

    return sorted(values_history, key=lambda i: i['date'])
