"""
Modelo de Usuario
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class TipoUsuario(str, enum.Enum):
    normal = "normal"
    admin = "admin"

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False, index=True)
    contrasena_hash = Column(String(255), nullable=False)
    moneda_preferida = Column(String(10))
    fecha_registro = Column(DateTime, default=func.now())
    foto_perfil = Column(String(255))
    tipo_usuario = Column(Enum(TipoUsuario), default=TipoUsuario.normal)
    
    # Relaciones
    grupos_creados = relationship("Grupo", back_populates="creador")
    gastos = relationship("Gasto", back_populates="usuario")
    ingresos = relationship("Ingreso", back_populates="usuario")
    metas_personales = relationship("Meta", back_populates="usuario")
    categorias_personales = relationship("Categoria", back_populates="usuario")
    historial_ai = relationship("HistorialAI", back_populates="usuario")
    aportes_metas = relationship("AporteMeta", back_populates="usuario")
    usuarios_grupos = relationship("UsuarioGrupo", back_populates="usuario")
