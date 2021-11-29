from uuid import UUID

from bson.objectid import ObjectId
from loguru import logger

from api.db.config import database, field_helper
from api.service.map import calculate_area

field_collection = database.get_collection("fields_collection")


# Retrieve all fields present in the database
async def retrieve_fields(user_id: str):
    fields = []
    async for field in field_collection.find({"user_id": user_id}):
        fields.append(field_helper(field))
    return fields


# Add a new field into to the database
async def add_field(field_data: dict) -> dict:
    field = await field_collection.insert_one(field_data)
    new_field = await field_collection.find_one({"_id": field.inserted_id})
    return field_helper(new_field)


# Retrieve a field with a matching ID
async def retrieve_field(id: str) -> dict:
    field = await field_collection.find_one({"_id": ObjectId(id)})
    if field:
        return field_helper(field)

# Retrieve a field with a matching ID
async def verify_unique_field_by_name(name: str, user_id: str) -> dict:
    field = await field_collection.find_one({"name": name, "user_id": user_id})
    if field:
        return False
    return True


# Update a field with a matching ID
async def update_field(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    field = await field_collection.find_one({"_id": ObjectId(id)})
    if field:
        updated_field = await field_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_field:
            return True
        return False


async def delete_field(id: UUID):
    field = await field_collection.find_one({"_id": ObjectId(id)})
    if field:
        await field_collection.delete_one({"_id": ObjectId(id)})
        return True
    return False


def generate_geojson(fields):
    features = []
    logger.info(fields)
    for field in fields:
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "area": calculate_area(field['coordinates']),
                    "id": field['id'],
                    "name": field['name']
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[coordinate['lng'], coordinate['lat']] for coordinate
                         in field["coordinates"]]
                    ]
                }
            }
        )
    return {
        "type": "FeatureCollection",
        "features": features
    }
