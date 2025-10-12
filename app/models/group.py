"""
Modelo de Grupo
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Grupo(Base):
    __tablename__ = "grupos"
    
    id_grupo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_creacion = Column(DateTime, default=func.now())
    creado_por = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    
    # Relaciones
    creador = relationship("Usuario", back_populates="grupos_creados")
    gastos = relationship("Gasto", back_populates="grupo")
    ingresos = relationship("Ingreso", back_populates="grupo")
    metas_grupales = relationship("Meta", back_populates="grupo")
    usuarios_grupos = relationship("UsuarioGrupo", back_populates="grupo")
