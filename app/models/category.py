"""
Modelo de Categoría
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class TipoCategoria(str, enum.Enum):
    ingreso = "ingreso"
    gasto = "gasto"

class Categoria(Base):
    __tablename__ = "categorias"
    
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    tipo = Column(Enum(TipoCategoria))
    color = Column(String(20))
    icono = Column(String(100))
    es_global = Column(Boolean, default=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="categorias_personales")
    gastos = relationship("Gasto", back_populates="categoria")
    ingresos = relationship("Ingreso", back_populates="categoria")
