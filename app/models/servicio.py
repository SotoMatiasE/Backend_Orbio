from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Servicio(Base):
    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    precio = Column(Float, nullable=False)
    duracion = Column(Integer, nullable=False)
    direccion = Column(String)  # 👈 agregá esta línea

    empleado_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    negocio_id = Column(Integer, ForeignKey("negocios.id"))

    empleado = relationship("User", back_populates="servicios", foreign_keys=[empleado_id])
    negocio = relationship("Negocio", back_populates="servicios", foreign_keys=[negocio_id])
