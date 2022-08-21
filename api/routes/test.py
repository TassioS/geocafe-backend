from fastapi import APIRouter
from fastapi import Response
import os, json

test_router = APIRouter()

@test_router.get("/")
async def home():
    img_folder_path = r'images/'
    dirListing = os.listdir(img_folder_path)
    responseDict = {
    "count" : len(dirListing),
    "files" : dirListing
    }
    return Response(status_code=200, content=json.dumps(responseDict, indent = 4))