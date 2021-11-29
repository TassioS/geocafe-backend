from datetime import datetime
from typing import List

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse

from api.models.field import (
    Field
)
from api.schemas import ResponseSingleModel, ResponseMultipleModel, Info, \
    FieldCreate
from api.service.field import (
    add_field,
    delete_field,
    retrieve_field,
    retrieve_fields,
    update_field, generate_geojson, verify_unique_field_by_name
)
from api.service.image_treatment import crop_image
from api.service.map import retrieve_dates, calculate_stats_from_area

field_router = APIRouter()


@field_router.post("/", tags=["Field"],
                   response_description="field data added into the database")
async def add_field_data(fields: List[FieldCreate]):
    new_fields = []
    fields_are_valid = True
    for field in fields:
        fields_are_valid = await verify_unique_field_by_name(field.name,
                                                       field.user_id)
        if not fields_are_valid:
            break
    if fields_are_valid:
        for field in fields:
            field.created_at = datetime.now()
            field = jsonable_encoder(field)
            new_field = await add_field(field)
            new_fields.append(new_field)

        return ResponseMultipleModel(success=True, data=new_fields,
                                     message="field added successfully.")
    else:
        return ResponseSingleModel(
            message="Fields not unique",
            success=False, data={}
        )


@field_router.get("/", tags=["Field"], response_description="fields retrieved")
async def get_fields(user_id: str):
    fields = await retrieve_fields(user_id)
    if fields:
        response = generate_geojson(fields)
        return ResponseSingleModel(success=True, data={"fields": fields,
                                                       "geojson": response},
                                   message="fields data retrieved successfully")

    return ResponseSingleModel(
        message="No fields found",
        success=False, data={"fields": []}
    )


@field_router.get("/{id}", tags=["Field"],
                  response_description="field data retrieved")
async def get_field_data(id):
    field = await retrieve_field(id)
    if field:
        return ResponseSingleModel(success=True, data=field,
                                   message="field data retrieved successfully")
    return ResponseSingleModel(success=False, message="An error occurred.",
                               data="field doesn't exist.")


@field_router.put("/{id}", tags=["Field"])
async def update_field_data(id: str, req: Field):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_field = await update_field(id, req)
    if updated_field:
        return ResponseSingleModel(
            success=True,
            data="field with ID: {} name update is successful".format(id),
            message="field name updated successfully",
        )
    return ResponseSingleModel(
        message="An error occurred",
        success=False, data="There was an error updating the field data.",
    )


@field_router.delete("/{id}", tags=["Field"],
                     response_description="field data deleted from the database")
async def delete_field_data(id: str):
    deleted_field = await delete_field(id)
    if deleted_field:
        return ResponseSingleModel(
            success=True,
            data={},
            message=f"field deleted successfully: field with ID: {id} removed"
        )
    return ResponseSingleModel(
        success=False,
        message=f"An error occurred: field with id {id} doesn't exist",
        data={}
    )


@field_router.get("/cut/user/{user_id}/{date}", tags=["Field"])
async def cut_field_image(user_id, date):
    fields = await retrieve_fields(user_id)
    if not date:
        date = retrieve_dates()[0].strftime("%d_%m_%Y")

    croped_image = crop_image(fields, date)
    return FileResponse(f"images/{croped_image}")


@field_router.get("/cut/{field_id}/{date}", tags=["Field"])
async def cut_field_image(field_id, date):
    field = await retrieve_field(field_id)
    if not date:
        date = retrieve_dates()[0].strftime("%d_%m_%Y")

    croped_image = crop_image([field], date)
    return FileResponse(f"images/{croped_image}")


@field_router.get("/map/dates", tags=["Field"])
async def get_maps_dates():
    dates = retrieve_dates()
    return ResponseSingleModel(
        success=True,
        data={"dates": dates},
        message="Map dates retrieved successful"
    )


@field_router.post("/info", tags=["Field"],
                   response_description="Get field info")
async def get_info(stats_data: Info):
    field = await retrieve_field(stats_data.field_id)
    stats = calculate_stats_from_area(field['coordinates'], field['name'],
                                      stats_data.date)
    if stats:
        return ResponseSingleModel(success=True, data=stats,
                                   message="Field info retrieved successfully")

    return ResponseSingleModel(
        message="Error calculating info",
        success=False, data={}
    )
