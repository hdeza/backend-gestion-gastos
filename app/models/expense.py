"""
Modelo de Gasto
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class MetodoPago(str, enum.Enum):
    efectivo = "efectivo"
    tarjeta = "tarjeta"
    transferencia = "transferencia"
    otro = "otro"

class Gasto(Base):
    __tablename__ = "gastos"
    
    id_gasto = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    monto = Column(DECIMAL(12, 2), nullable=False)
    fecha = Column(Date, nullable=False)
    metodo_pago = Column(Enum(MetodoPago))
    nota = Column(Text)
    recurrente = Column(Boolean, default=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"))
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="gastos")
    usuario = relationship("Usuario", back_populates="gastos")
    grupo = relationship("Grupo", back_populates="gastos")
