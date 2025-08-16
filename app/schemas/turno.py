from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional

class TurnoBase(BaseModel):
    dia: date
    hora_inicio: time
    hora_fin: time
    cliente_nombre: str
    cliente_email: Optional[EmailStr] = None
    cliente_telefono: Optional[str] = None
    metodo_pago: str
    monto_pagado: float
    estado: str

class TurnoCreate(TurnoBase):
    servicio_id: int
    empleado_id: int

class TurnoUpdate(BaseModel):
    dia: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    estado: Optional[str] = None

class ShowTurno(TurnoBase):
    id: int
    servicio_id: int
    empleado_id: int

    class Config:
        orm_mode = True
