"""
Modelo de Ingreso
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.core.database import Base

class Ingreso(Base):
    __tablename__ = "ingresos"
    
    id_ingreso = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    monto = Column(DECIMAL(12, 2), nullable=False)
    fecha = Column(Date, nullable=False)
    fuente = Column(String(100))
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"))
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="ingresos")
    usuario = relationship("Usuario", back_populates="ingresos")
    grupo = relationship("Grupo", back_populates="ingresos")
