# esquema para servicio

from pydantic import BaseModel

class ServicioBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    precio: float

class ServicioCreate(ServicioBase):
    negocio_id: int

class ServicioUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    precio: float | None = None

class ShowServicio(ServicioBase):
    id: int
    negocio_id: int
    class Config:
        orm_mode = True
