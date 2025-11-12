"""
Modelo de Invitación a Grupo
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import secrets

class EstadoInvitacion(str, enum.Enum):
    pendiente = "pendiente"
    aceptada = "aceptada"
    rechazada = "rechazada"
    expirada = "expirada"

class Invitacion(Base):
    __tablename__ = "invitaciones"
    
    id_invitacion = Column(Integer, primary_key=True, index=True)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"), nullable=False)
    token = Column(String(64), unique=True, nullable=False, index=True)
    creado_por = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_usuario_invitado = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    estado = Column(Enum(EstadoInvitacion), default=EstadoInvitacion.pendiente)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_expiracion = Column(DateTime, nullable=True)
    fecha_aceptacion = Column(DateTime, nullable=True)
    usado = Column(Boolean, default=False)
    
    # Relaciones
    grupo = relationship("Grupo", back_populates="invitaciones")
    creador = relationship("Usuario", foreign_keys=[creado_por], back_populates="invitaciones_creadas")
    usuario_invitado = relationship("Usuario", foreign_keys=[id_usuario_invitado], back_populates="invitaciones_recibidas")
    
    @staticmethod
    def generar_token() -> str:
        """Generar un token único para la invitación"""
        return secrets.token_urlsafe(32)

