from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict
#from sqlalchemy.sql.sqltypes import Date
from datetime import date
from sqlalchemy import CheckConstraint

#__________________3.12.A&A_______________________________________________________________________________________
class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    avatar: str

    class Config:
        from_attributes = True
        
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

#__________________1.13.Email_____________________    
class RequestEmail(BaseModel):
    email: EmailStr