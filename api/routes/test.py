from fastapi import APIRouter
from fastapi import Response
import os, json

test_router = APIRouter()

@test_router.get("/")
async def home():
    import boto3
    session = boto3.session.Session()

    s3 = session.client(
    service_name='s3',
    aws_access_key_id='AKIA3ED3KLXYUOMRUTS7',
    aws_secret_access_key='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'
    )

    with open('./images/STA_NDVI_06_09_2022_03:10:15.tif', 'wb') as f:
        s3.download_fileobj('scheduler-test-tfg', 'STA_NDVI_06_09_2022_03:10:15.tif', f)

    img_folder_path = r'images/'
    dirListing = os.listdir(img_folder_path)
    responseDict = {
    "count" : len(dirListing),
    "files" : dirListing
    }
    return Response(status_code=200, content=json.dumps(responseDict, indent = 4))