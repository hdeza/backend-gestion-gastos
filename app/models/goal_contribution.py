"""
Modelo de AporteMeta
"""
from sqlalchemy import Column, Integer, ForeignKey, Date, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class AporteMeta(Base):
    __tablename__ = "aportes_metas"
    
    id_aporte = Column(Integer, primary_key=True, index=True)
    id_meta = Column(Integer, ForeignKey("metas.id_meta"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    monto = Column(DECIMAL(12, 2), nullable=False)
    fecha = Column(Date, default=func.current_date())
    
    # Relaciones
    meta = relationship("Meta", back_populates="aportes")
    usuario = relationship("Usuario", back_populates="aportes_metas")
