from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class EmpleadoCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class EmpleadoOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr

    class Config:
        orm_mode = True
        
class EmpleadoUpdate(BaseModel):
    nombre: Optional[str]
    email: Optional[str]
    password: Optional[str]        