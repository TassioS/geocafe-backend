import motor.motor_asyncio
from decouple import config

MONGO_DETAILS = config('MONGO_DETAILS')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.tfg

user_collection = database.get_collection("users_collection")
field_collection = database.get_collection("field_collection")


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "created_at": user["created_at"]
    }


def field_helper(field) -> dict:
    return {
        "id": str(field["_id"]),
        "name": field["name"],
        "coordinates": field["coordinates"],
        "created_at": field["created_at"]
    }


def note_helper(field) -> dict:
    response = {"notes": field["notes"], "name": field["name"],
                "id": str(field["_id"])}
    return response
