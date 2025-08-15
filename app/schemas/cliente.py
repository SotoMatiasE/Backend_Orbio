from pydantic import BaseModel, EmailStr
from typing import Optional

class ClienteCreate(BaseModel):
    nombre: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None

class ClienteOut(BaseModel):
    id: int
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None

class Config:
    from_attributes = True
