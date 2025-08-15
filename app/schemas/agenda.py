from pydantic import BaseModel, EmailStr
from datetime import datetime, time
from typing import Optional, List

class ShowAgenda(BaseModel):
    id: int
    dia: str
    hora_inicio: time
    hora_fin: time
    duracion_turno: int

    class Config:
        form_mode = True