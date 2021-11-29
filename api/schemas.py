import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from api.models.field import Coordinate


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str


class ResponseSingleModel(BaseModel):
    data: Optional[dict]
    message: str
    success: bool


class ResponseMultipleModel(BaseModel):
    data: Optional[List[dict]]
    message: str
    success: bool


class Info(BaseModel):
    field_id: str
    date: str


class NoteData(BaseModel):
    field_id: str
    note: str


class NoteUpdate(NoteData):
    note_id: uuid.UUID


class FieldCreate(BaseModel):
    name: str
    user_id: str
    coordinates: List[Coordinate]
    created_at: Optional[datetime]
    notes = []
