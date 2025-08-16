from pydantic import BaseModel
from datetime import date, time

class ShowAgenda(BaseModel):
    id: int
    dia: date
    hora_inicio: time
    hora_fin: time
    duracion_turno: int

    class Config:
        orm_mode = True


class AgendaCreateEmpleado(BaseModel):
    dia: date
    hora_inicio: time
    hora_fin: time
    duracion_turno: int