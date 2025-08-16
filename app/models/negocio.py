from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Negocio(Base):
    __tablename__ = "negocios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    alias = Column(String, unique=True, nullable=False)
    direccion = Column(String, nullable=False)
    provincia = Column(String, nullable=False)
    dueño_id = Column(Integer, ForeignKey("users.id"))

    usuarios = relationship("User", back_populates="negocio", foreign_keys="User.negocio_id")
    dueño = relationship("User", foreign_keys=[dueño_id])
    servicios = relationship("Servicio", back_populates="negocio", foreign_keys="Servicio.negocio_id")
