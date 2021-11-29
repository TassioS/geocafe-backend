from datetime import timedelta

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status

from api.models.user import (
    User
)
from api.schemas import ResponseSingleModel, Token, ResponseMultipleModel, \
    Login
from api.service.auth import AuthService
from api.service.user import (
    add_user,
    delete_user,
    retrieve_user,
    retrieve_users,
    update_user,
)

user_router = APIRouter()
TOKEN_EXPIRE_MINUTES = 43200
auth_service = AuthService()


@user_router.post("/", tags=["User"],
                  response_description="user data added into the database")
async def add_user_data(user: User):
    user = jsonable_encoder(user)
    user['password'] = bcrypt.hashpw(user['password'].encode("utf-8"),
                                     bcrypt.gensalt())
    new_user = await add_user(user)
    return ResponseSingleModel(success=True, data=new_user,
                               message="user added successfully.")


@user_router.get("/", tags=["User"], response_description="users retrieved")
async def get_users():
    users = await retrieve_users()

    if users:
        return ResponseMultipleModel(success=True, data=users,
                                     message="users data retrieved successfully")


@user_router.get("/{id}", tags=["User"],
                 response_description="user data retrieved")
async def get_user_data(id):
    user = await retrieve_user(id)
    if user:
        return ResponseSingleModel(success=True, data=user,
                                   message="user data retrieved successfully")
    return ResponseSingleModel(success=False, message="An error occurred.",
                               data="user doesn't exist.")


@user_router.put("/{id}", tags=["User"])
async def update_user_data(id: str, req: User):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_user = await update_user(id, req)
    if updated_user:
        return ResponseSingleModel(
            success=True,
            message="user with ID: {} name update is successful".format(id),
        )
    return ResponseMultipleModel(
        success=False,
        message="An error occurred",
        data="There was an error updating the user data.",
    )


@user_router.delete("/{id}", tags=["User"],
                    response_description="user data deleted from the database")
async def delete_user_data(id: str):
    deleted_user = await delete_user(id)
    if deleted_user:
        return ResponseSingleModel(
            success=True,
            message="user with ID: {} removed".format(id)
        )
    return ResponseSingleModel(
        success=False,
        message="user with id {0} doesn't exist".format(id)
    )


@user_router.post("/login", tags=["User"], response_model=Token)
async def login_for_access_token(login: Login):
    user = await auth_service.authenticate_user(login.username,
                                                login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(
        data={
            "id": str(user['_id']),
            "email": user['email']
        },
        expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    return Token(access_token=access_token, token_type="bearer", user_id=str(user['_id']))



@user_router.post("/logout", tags=["User"], response_model=Token)
def logout(current_user: User = Depends(auth_service.current_user)):
    """
    return an empty token, assuming login and logout
    workflows are handled in a client
    """
    return Token(access_token="", token_type="bearer")
