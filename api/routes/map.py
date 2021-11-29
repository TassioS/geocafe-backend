from fastapi import APIRouter
from loguru import logger

from api.schemas import ResponseMultipleModel
from api.service.image_treatment import getPixelHistory

map_router = APIRouter()


@map_router.get("/history/point", tags=["Map"],
                response_description="field data added into the database")
async def pixel_history(lat: float, lon: float):
    try:
        value_history = getPixelHistory(lon, lat)
        return ResponseMultipleModel(success=True, data=value_history,
                                     message="Value history report found")
    except Exception as e:
        logger.error(f"Pixel history error:{e}")
