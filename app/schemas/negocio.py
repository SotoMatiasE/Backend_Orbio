#crear negocio y admin

from pydantic import BaseModel, EmailStr

class NegocioCreate(BaseModel):
    nombre: str
    alias: str
    direccion: str
    provincia: str
    admin_nombre: str
    admin_email: EmailStr
    admin_password: str

class NegocioUpdate(BaseModel):
    nombre: str | None = None
    alias: str | None = None
    direccion: str | None = None
    provincia: str | None = None