from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    empleado = "empleado"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    rol = Column(Enum(UserRole), nullable=False)
    negocio_id = Column(Integer, ForeignKey("negocios.id"), nullable=True)

    negocio = relationship("Negocio", back_populates="usuarios", foreign_keys=[negocio_id])
    servicios = relationship("Servicio", back_populates="empleado", foreign_keys="Servicio.empleado_id")


