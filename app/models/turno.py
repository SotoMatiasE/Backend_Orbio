from sqlalchemy import Column, Integer, String, Time, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.cliente import Cliente

class Turno(Base):
    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)
    dia = Column(Date, nullable=False)  # Solo fecha
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

    cliente_nombre = Column(String, nullable=False)
    cliente_email = Column(String, nullable=True)
    cliente_telefono = Column(String, nullable=True)
    metodo_pago = Column(String, nullable=False)
    monto_pagado = Column(Float, nullable=False)
    estado = Column(String, nullable=False)

    servicio_id = Column(Integer, ForeignKey("servicios.id"))
    empleado_id = Column(Integer, ForeignKey("users.id"))
    cliente_id = Column(Integer, ForeignKey("clientes.id"))

    cliente = relationship("Cliente", backref="turnos")
