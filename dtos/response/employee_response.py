from pydantic import BaseModel, EmailStr
from datetime import date


class CreateEmployeeResponseDTO(BaseModel):
    id: str
    name: str
    email: EmailStr
    department: str
    date_joined: date


class UpdateEmployeeResponseDTO(BaseModel):
    id: str
    name: str
    email: EmailStr
    department: str
    date_joined: date


class GetEmployeeResponseDTO(BaseModel):
    id: str
    name: str
    email: EmailStr
    department: str
    date_joined: date


class GetAllEmployeesResponseDTO(BaseModel):
    id: str
    name: str
    email: EmailStr
    department: str
    date_joined: date


class DeleteEmployeeResponseDTO(BaseModel):
    message: str
