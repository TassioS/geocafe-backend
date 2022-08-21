from fastapi import APIRouter
from fastapi import Response
import os

test_router = APIRouter()

@test_router.get("/")
async def home():
    img_folder_path = r'images/'
    dirListing = os.listdir('../../images/')
    responseDict = {
    "count" : len(dirListing),
    "files" : dirListing
    }
    return Response(status_code=200, content=responseDict)