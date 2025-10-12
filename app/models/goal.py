"""
Modelo de Meta
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class EstadoMeta(str, enum.Enum):
    activa = "activa"
    completada = "completada"
    cancelada = "cancelada"

class Meta(Base):
    __tablename__ = "metas"
    
    id_meta = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    monto_objetivo = Column(DECIMAL(12, 2), nullable=False)
    monto_acumulado = Column(DECIMAL(12, 2), default=0)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    estado = Column(Enum(EstadoMeta))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"))
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="metas_personales")
    grupo = relationship("Grupo", back_populates="metas_grupales")
    aportes = relationship("AporteMeta", back_populates="meta")
