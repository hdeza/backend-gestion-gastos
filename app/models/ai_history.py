"""
Modelo de HistorialAI
"""
from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class TipoHistorial(str, enum.Enum):
    recomendacion = "recomendacion"
    alerta = "alerta"
    analisis = "analisis"

class HistorialAI(Base):
    __tablename__ = "historial_ai"
    
    id_historial = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    tipo = Column(Enum(TipoHistorial))
    contenido = Column(Text, nullable=False)
    fecha = Column(DateTime, default=func.now())
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="historial_ai")
