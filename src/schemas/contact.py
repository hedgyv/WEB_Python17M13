from typing import Optional

from pydantic import BaseModel, EmailStr, Field
#from sqlalchemy.sql.sqltypes import Date
from datetime import date, datetime
from sqlalchemy import CheckConstraint
from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    f_name: str = Field(min_length=3, max_length=50)
    l_name: str = Field(min_length=3, max_length=50)
    email: str = EmailStr
    phone: str = Field(min_length=3, max_length=25)
    birthday: date
    additional_data: str = None


class ContactUpdateSchema(ContactSchema):
    completed: bool


class ContactResponse(BaseModel):
    id: int = 1
    f_name: str
    l_name: str
    email: str
    phone: str
    birthday: date
    additional_data: str = None
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None  #если заккоментить, get возвращается без юзера
    
    class Config:
        from_attributes = True