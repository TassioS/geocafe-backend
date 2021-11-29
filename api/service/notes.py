import uuid

from bson.objectid import ObjectId

from api.db.config import database, note_helper
from api.schemas import NoteData

field_collection = database.get_collection("fields_collection")


async def retrieve_notes(user_id: str):
    notes = []
    async for field in field_collection.find({"user_id": user_id}):
        if field['notes']:
            notes.append(note_helper(field))
    return notes


async def add_note(note_data: NoteData):
    field = await field_collection.find_one(
        {"_id": ObjectId(note_data.field_id)})
    if field:
        updated_field = await field_collection.update_one(
            {"_id": ObjectId(note_data.field_id)}, {'$push': {
                'notes': {'id': uuid.uuid4(), 'text': note_data.note}}}
        )
        if updated_field:
            return True
    return False


async def update_note(field_id: str, text: str, note_id: uuid.UUID):
    if await delete_note(field_id, note_id):
        if await add_note(NoteData(field_id=field_id, note=text)):
            return True
    return False


async def delete_note(field_id: str, note_id: uuid.UUID):
    field = await field_collection.find_one({"_id": ObjectId(field_id)})
    if field:
        for note in field["notes"]:
            if note["id"] == note_id:
                await field_collection.update_one(
                    {"_id": ObjectId(field_id)}, {'$pull': {
                        'notes': note}}
                )

        return True
