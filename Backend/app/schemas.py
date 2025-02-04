from pydantic import BaseModel, EmailStr, ConfigDict, constr
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str]
    name: Optional[str]