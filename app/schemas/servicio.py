from pydantic import BaseModel
from typing import Optional

class ServicioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    direccion: str  # 👈 agregado aquí

class ServicioCreate(ServicioBase):
    negocio_id: int
    duracion: int

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    duracion: Optional[int] = None
    direccion: Optional[str] = None  # 👈 también aquí

class ShowServicio(ServicioBase):
    id: int
    negocio_id: int
    duracion: int  # 👈 si lo querés mostrar
    empleado_id: int

    class Config:
        orm_mode = True

class ServicioOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    duracion: int
    direccion: str  # 👈 agregado aquí también
    negocio_id: int
    empleado_id: int

    class Config:
        orm_mode = True
