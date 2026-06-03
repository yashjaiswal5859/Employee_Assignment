from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date
from typing import Optional

class CreateEmployeeRequestDTO(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    department: str = Field(..., min_length=2)
    date_joined: date

    @field_validator('date_joined', mode='before')
    def validate_date_format(cls, v):
        if isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except ValueError:
                raise ValueError('Date must be in format YYYY-MM-DD')
        return v

    @field_validator('date_joined')
    def validate_not_future(cls, v):
        if v > date.today():
            raise ValueError('Date joined cannot be in the future')
        return v

class UpdateEmployeeRequestDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, min_length=2)
    date_joined: Optional[date] = None

    @field_validator('date_joined', mode='before')
    def validate_date_format(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except ValueError:
                raise ValueError('Date must be in format YYYY-MM-DD')
        return v

    @field_validator('date_joined')
    def validate_not_future(cls, v):
        if v is not None and v > date.today():
            raise ValueError('Date joined cannot be in the future')
        return v
