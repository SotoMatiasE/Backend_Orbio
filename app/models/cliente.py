from sqlalchemy import Column, Integer, String
from app.db.session import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=False)
    telefono = Column(String, nullable=True, unique=False)
