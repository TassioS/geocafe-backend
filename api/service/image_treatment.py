import os
from time import sleep
import uuid
from datetime import datetime

import rasterio
import rasterio.features
import rasterio.warp
from rasterio.mask import mask as rast_mask

import boto3
from decouple import config

def download_dir(client, resource, dist, local='/tmp', bucket='your_bucket'):
    paginator = client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=dist):
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                download_dir(client, resource, subdir.get('Prefix'), local, bucket)
        for file in result.get('Contents', []):
            dest_pathname = os.path.join(local, file.get('Key'))
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
            if not file.get('Key').endswith('/'):
                resource.meta.client.download_file(bucket, file.get('Key'), dest_pathname)

def download_all_images():
    session = boto3.session.Session()

    client = session.client(
    service_name='s3',
    aws_access_key_id=config('aws_access_key_id'),
    aws_secret_access_key=config('aws_secret_access_key')
    )

    resource = boto3.resource(service_name='s3',
    aws_access_key_id=config('aws_access_key_id'),
    aws_secret_access_key=config('aws_secret_access_key')
        )

    download_dir(client, resource, '', 'images/', bucket='scheduler-test-tfg')

def get_image_from_s3(date):
    img_name = f"STA_NDVI_{date}.tif"
    img_path = f"images/{img_name}"

    try:
        f = open(img_path)
        print('Imagem já existe no diretorio /images')
        return
    except IOError:
        print("Imagem não encontrada no diretorio. Iniciando download do s3")

    session = boto3.session.Session()

    s3 = session.client(
    service_name='s3',
    aws_access_key_id=config('aws_access_key_id'),
    aws_secret_access_key=config('aws_secret_access_key')
    )

    with open(img_path, 'wb') as f:
        s3.download_fileobj('bucket-regador', img_name, f)


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
    get_image_from_s3(date)
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
