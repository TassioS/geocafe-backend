from uuid import UUID

from fastapi import APIRouter

from api.schemas import ResponseSingleModel, NoteData, NoteUpdate, \
    ResponseMultipleModel
from api.service.notes import retrieve_notes, add_note, delete_note, \
    update_note

note_router = APIRouter()


@note_router.get("", tags=["Note"],
                 response_description="notes retrieved")
async def get_notes(user_id: str):
    notes = await retrieve_notes(user_id)
    if notes:
        return ResponseMultipleModel(success=True, data=notes,
                                     message="notes data retrieved successfully")

    return ResponseMultipleModel(
        message="No notes found",
        success=False, data=[]
    )


@note_router.post(
    "", tags=["Note"],
    response_description="field note data added into the database")
async def add_note_to_field(note_data: NoteData):
    note = await add_note(note_data)
    if note:
        return ResponseSingleModel(success=True,
                                   message="note created successfully")

    return ResponseSingleModel(
        message="Note creation failed",
        success=False, data={"fields": []}
    )


@note_router.put(
    "", tags=["Note"],
    response_description="field note data added into the database")
async def update_note_from_field(note_data: NoteUpdate):
    note = await update_note(note_data.field_id, note_data.note,
                             note_data.note_id)
    if note:
        return ResponseSingleModel(success=True,
                                   message="notes deleted successfully")

    return ResponseSingleModel(
        message="Note delete failed",
        success=False, data={"fields": []}
    )


@note_router.delete(
    "/{field_id}/{note_id}", tags=["Note"],
    response_description="field note data added into the database")
async def remove_note_from_field(field_id: str, note_id: UUID):
    note = await delete_note(field_id, note_id)
    if note:
        return ResponseSingleModel(success=True,
                                   message="notes deleted successfully")

    return ResponseSingleModel(
        message="Note delete failed",
        success=False, data={"fields": []}
    )
