"""
Modelo de UsuarioGrupo
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class RolGrupo(str, enum.Enum):
    miembro = "miembro"
    admin = "admin"

class UsuarioGrupo(Base):
    __tablename__ = "usuarios_grupos"
    
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), primary_key=True)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"), primary_key=True)
    rol = Column(Enum(RolGrupo), default=RolGrupo.miembro)
    fecha_union = Column(DateTime, default=func.now())
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="usuarios_grupos")
    grupo = relationship("Grupo", back_populates="usuarios_grupos")
