from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class Coordinate(BaseModel):
    lat: float
    lng: float


class Note(BaseModel):
    id: UUID
    text: str


class Field(BaseModel):
    """
    The Field model
    """

    name: str
    user_id: str
    coordinates: List[Coordinate]
    notes: List[Note]
    created_at: Optional[datetime]
