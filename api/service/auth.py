from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from pydantic import EmailStr
from starlette import status

# from config import apisecrets, oauth2_scheme
from api.db.config import database
from api.service.user import retrieve_user

user_collection = database.get_collection("users_collection")

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
# SECRET_KEY = apisecrets.SECRET_KEY
SECRET_KEY = "/n@bS@%6dzBP$`)"
ACCESS_TOKEN_ALGORITHM = 'HS256'
CREDENTIALS_EXCEPTION = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                      detail="Invalid credentials.",
                                      headers={"WWW-Authenticate": "Bearer"})

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class AuthService:
    def valid_password(self, plain_pass: str, hashed_pass: str):
        return bcrypt.hashpw(plain_pass.encode("utf-8"),
                             hashed_pass) == hashed_pass

    async def authenticate_user(self, email: str, password: str):
        user = await user_collection.find_one({"email": email})
        if not user:
            return
        if not self.valid_password(password, user['password']):
            return
        return user

    def create_access_token(self, data: dict,
                            expires_delta: timedelta) -> bytes:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode,
                                 SECRET_KEY,
                                 algorithm=ACCESS_TOKEN_ALGORITHM)
        return encoded_jwt

    def current_user(self, token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token,
                                 SECRET_KEY,
                                 algorithms=[ACCESS_TOKEN_ALGORITHM])
            id = payload.get("id")
        except PyJWTError:
            raise CREDENTIALS_EXCEPTION
        return retrieve_user(id)
