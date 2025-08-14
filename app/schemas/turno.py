from pydantic import BaseModel, EmailStr
from datetime import datetime, time
from typing import Optional

class TurnoBase(BaseModel):
    fecha: datetime
    cliente_nombre: str
    cliente_email: Optional[EmailStr] = None
    cliente_telefono: Optional[str] = None
    metodo_pago: str  # ejemplo: "paypal", "mercado_pago", "local"
    monto_pagado: float
    estado: str  # "pendiente", "confirmado", "cancelado"

class TurnoCreate(TurnoBase):
    servicio_id: int
    empleado_id: int

class TurnoUpdate(BaseModel):
    fecha: Optional[datetime] = None
    estado: Optional[str] = None

class ShowTurno(TurnoBase):
    id: int
    servicio_id: int
    empleado_id: int
    class Config:
        orm_mode = True

class TurnoEmpleadoUpdate(BaseModel):
    estado: Optional[str] = None
    fecha: Optional[datetime] = None