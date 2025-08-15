from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime, time

class EmpleadoCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    negocio_id: int

class EmpleadoOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr

    class Config:
        form_mode = True
        
class EmpleadoUpdate(BaseModel):
    nombre: Optional[str]
    email: Optional[str]
    password: Optional[str]

class AgendaCreateEmpleado(BaseModel):
    dia: str
    hora_inicio: time
    hora_fin: time
    duracion_turno: int  # en minutos

class ServicioEmpleado(BaseModel):
    nombre: str
    precio: float
    descripcion: Optional[str] = None
    duracion: int  # duración en minutos

class ServicioUpdateEmpleado(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[float] = None
    descripcion: Optional[str] = None
    duracion: Optional[int] = None