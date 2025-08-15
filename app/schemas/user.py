from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    empleado = "empleado"

class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: UserRole
    negocio_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ShowUser(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: UserRole

    class Config:
        form_mode = True