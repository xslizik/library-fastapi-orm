from pydantic import BaseModel, validator
from datetime import datetime,timezone
from fastapi import status, HTTPException
from typing import Optional
from uuid import UUID
import re

from .models import instance_types, instance_statuses, card_statuses, rental_statuses

# DEFAULT SCHEMAS
class Request(BaseModel):
    id: Optional[str] = None

    @validator('id', pre=True)
    def validate_id(cls, value):
        try:
            UUID(value)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value
class Response(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime

    @validator('created_at', 'updated_at')
    def format_created_at(cls, value):
        dt_utc = value.astimezone(timezone.utc)
        return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    class Config:
        orm_mode = True

# CATEGORY
class CategoryRequest(Request):
    name: str

    @validator('name', pre=True, always=True)
    def validate_str(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value
class CategoryResponse(Response):
    name: str

# AUTHOR
class AuthorRequest(Request):
    name: str
    surname: str

    @validator('name', 'surname', pre=True, always=True)
    def validate_str(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value
class AuthorPatch(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None

    @validator('name', 'surname', pre=True)
    def validate_str(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value
class AuthorResponse(Response):
    name: str
    surname: str

# PUBLICATION
class PublicationRequest(Request):
    title : str
    authors: list[dict[str, str]]
    categories: list[str]

    @validator('title', pre=True, always=True)
    def validate_str(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('authors', pre=True, always=True)
    def validate_authors(cls, authors: list):
        if authors:
            for author in authors:
                if not isinstance(author["name"], str) or not isinstance(author["surname"], str):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return authors

    @validator('categories', pre=True, always=True)
    def validate_str_list(cls, values: list):
        if values:
            for value in values:
                if not isinstance(value, str):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return values
class PublicationResponse(Response):
    title : str
    authors: list[dict[str, str]]
    categories: list[str]

# INSTANCE
class InstanceRequest(Request):
    type : Optional[str] = None
    publisher : Optional[str] = None
    year : Optional[int] = None
    status: Optional[str] = "available"
    publication_id : Optional[str] = None

    @validator('publication_id')
    def validate_id(cls, value):
        try:
            UUID(value)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('publisher')
    def validate_str(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('year')
    def validate_int(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('type')
    def validate_type(cls, value):
        if value not in instance_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('status')
    def validate_status(cls, value):
        if value not in instance_statuses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value
class InstanceResponse(Response):
    type : str
    publisher : str
    year : int
    status : str
    publication_id :str

# CARD
class CardRequest(Request):
    user_id : str
    magstripe : Optional[str] = None
    status : str

    @validator('user_id', pre=True, always=True)
    def validate_id(cls, value):
        try:
            UUID(value)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('magstripe', pre=True)
    def validate_magstripe(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if not len(value) == 20:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('status', pre=True, always=True)
    def validate_status(cls, value):
        if value not in card_statuses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

class CardPatch(Request):
    user_id : Optional[str] = None
    magstripe : Optional[str] = None
    status : Optional[str] = None

    @validator('user_id', pre=True)
    def validate_id(cls, value):
        try:
            UUID(value)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('magstripe', pre=True)
    def validate_magstripe(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if not len(value) == 20:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('status', pre=True)
    def validate_status(cls, value):
        if value not in card_statuses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

class CardResponse(Response):
    user_id : str
    magstripe : str
    status : str

# RENTAL
class RentalRequest(Request):
    user_id : str
    publication_id : str
    duration : int

    @validator('user_id', 'publication_id', pre=True, always=True)
    def validate_id(cls, value):
        try:
            UUID(value)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('duration', pre=True, always=True)
    def validate_int(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if value <= 0 or value > 14:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value
class RentalResponse(BaseModel):
    id : str
    user_id : str
    publication_instance_id : str
    duration : int
    start_date : datetime
    end_date : datetime
    status : str

    @validator('start_date', 'end_date')
    def format_created_at(cls, value):
        dt_utc = value.astimezone(timezone.utc)
        return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    class Config:
        orm_mode = True
class RentalPatch(BaseModel):
    duration: int

    @validator('duration', pre=True, always=True)
    def validate_int(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if value <= 0 or value > 14:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

# RESERVATION
class ReservationRequest(Request):
    user_id : str
    publication_id : str

    @validator('user_id', 'publication_id', pre=True, always=True)
    def validate_id(cls, value):
        try:
            UUID(value)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value
class ReservationResponse(BaseModel):
    id : str
    user_id : str
    publication_id : str
    created_at : datetime

    @validator('created_at')
    def format_created_at(cls, value):
        dt_utc = value.astimezone(timezone.utc)
        return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    class Config:
        orm_mode = True

# USER
class UserRequest(Request):
    name : str
    surname : str
    email : str
    birth_date : str
    personal_identificator : str

    @validator('name', 'surname', 'personal_identificator', pre=True, always=True)
    def validate_str(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('email', pre=True, always=True)
    def validate_email(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        pattern = r'^\S+@\S+\.\S+$'
        if not bool(re.match(pattern, value)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('birth_date', pre=True, always=True)
    def validate_date(cls, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return value
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

class UserPatch(Request):
    name : Optional[str] = None
    surname : Optional[str] = None
    email : Optional[str] = None
    birth_date : Optional[str] = None
    personal_identificator : Optional[str] = None

    @validator('name', 'surname', 'personal_identificator', pre=True)
    def validate_str(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('email', pre=True)
    def validate_email(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        pattern = r'^\S+@\S+\.\S+$'
        if not bool(re.match(pattern, value)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return value

    @validator('birth_date', pre=True)
    def validate_date(cls, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return value
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

class UserResponse(Response):
    name : str
    surname : str
    email : str
    birth_date : datetime
    personal_identificator : str

    @staticmethod
    def to_date_format(dt: datetime) -> str:
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.strftime('%Y-%m-%d')

    @validator('birth_date')
    def format_birth(cls, value):
        return cls.to_date_format(value)
