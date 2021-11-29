from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """
    The User model
    """

    email: EmailStr
    password: str
    created_at: Optional[datetime] = datetime.now()

