# modelo Servicio

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.session import Base

class Servicio(Base):
    __tablename__ = "servicios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, nullable=False)
    duracion = Column(Integer, nullable=False)
    negocio_id = Column(Integer, ForeignKey("negocios.id"))
    empleado_id = Column(Integer, ForeignKey("users.id"))