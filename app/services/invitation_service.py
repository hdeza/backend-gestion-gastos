"""
Servicio para gestión de invitaciones
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import base64
import io
from app.models.invitation import Invitacion, EstadoInvitacion
from app.models.group import Grupo
from app.models.user_group import UsuarioGrupo, RolGrupo
from app.schemas.invitation import InvitacionCreate
from app.core.config import settings

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


class InvitationService:
    """Servicio para operaciones de invitaciones"""

    def __init__(self, db: Session):
        self.db = db
        self.base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')

    def create_invitation(self, invitation_data: InvitacionCreate, creator_id: int) -> Invitacion:
        """Crear nueva invitación con token único"""
        # Verificar que el creador es admin del grupo
        if not self._is_group_admin(invitation_data.id_grupo, creator_id):
            raise ValueError("Solo los administradores pueden crear invitaciones")

        # Generar token único
        token = Invitacion.generar_token()
        
        # Calcular fecha de expiración
        fecha_expiracion = None
        if invitation_data.dias_expiracion:
            fecha_expiracion = datetime.utcnow() + timedelta(days=invitation_data.dias_expiracion)

        db_invitation = Invitacion(
            id_grupo=invitation_data.id_grupo,
            token=token,
            creado_por=creator_id,
            id_usuario_invitado=invitation_data.id_usuario_invitado,
            estado=EstadoInvitacion.pendiente,
            fecha_expiracion=fecha_expiracion
        )

        self.db.add(db_invitation)
        self.db.commit()
        self.db.refresh(db_invitation)
        return db_invitation

    def get_invitation_by_token(self, token: str) -> Optional[Invitacion]:
        """Obtener invitación por token"""
        invitation = self.db.query(Invitacion).filter(
            Invitacion.token == token
        ).first()

        if not invitation:
            return None

        # Verificar si está expirada
        if invitation.fecha_expiracion and invitation.fecha_expiracion < datetime.utcnow():
            if invitation.estado == EstadoInvitacion.pendiente:
                invitation.estado = EstadoInvitacion.expirada
                self.db.commit()
            return None

        return invitation

    def get_invitation_link(self, token: str) -> str:
        """Generar link de invitación"""
        return f"{self.base_url}/invitation/{token}"

    def generate_qr_code(self, token: str) -> Optional[str]:
        """Generar código QR en base64 para la invitación"""
        if not QR_AVAILABLE:
            return None

        try:
            link = self.get_invitation_link(token)
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(link)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            qr_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            return qr_base64
        except Exception as e:
            print(f"Error generando QR: {e}")
            return None

    def accept_invitation(self, token: str, user_id: int) -> bool:
        """Aceptar invitación y agregar usuario al grupo"""
        invitation = self.get_invitation_by_token(token)
        
        if not invitation:
            return False

        if invitation.estado != EstadoInvitacion.pendiente:
            return False

        # Verificar que el usuario no esté ya en el grupo
        if self._is_user_in_group(invitation.id_grupo, user_id):
            return False

        # Agregar usuario al grupo
        usuario_grupo = UsuarioGrupo(
            id_usuario=user_id,
            id_grupo=invitation.id_grupo,
            rol=RolGrupo.miembro
        )
        self.db.add(usuario_grupo)

        # Actualizar estado de la invitación
        invitation.estado = EstadoInvitacion.aceptada
        invitation.fecha_aceptacion = datetime.utcnow()
        invitation.usado = True

        self.db.commit()
        return True

    def reject_invitation(self, token: str, user_id: int) -> bool:
        """Rechazar invitación"""
        invitation = self.get_invitation_by_token(token)
        
        if not invitation:
            return False

        if invitation.estado != EstadoInvitacion.pendiente:
            return False

        invitation.estado = EstadoInvitacion.rechazada
        self.db.commit()
        return True

    def get_group_invitations(self, group_id: int, user_id: int) -> list:
        """Obtener todas las invitaciones de un grupo (solo admin)"""
        if not self._is_group_admin(group_id, user_id):
            return []

        return self.db.query(Invitacion).filter(
            Invitacion.id_grupo == group_id
        ).all()

    def revoke_invitation(self, invitation_id: int, group_id: int, user_id: int) -> bool:
        """Revocar una invitación (solo admin)"""
        if not self._is_group_admin(group_id, user_id):
            return False

        invitation = self.db.query(Invitacion).filter(
            Invitacion.id_invitacion == invitation_id,
            Invitacion.id_grupo == group_id
        ).first()

        if not invitation:
            return False

        if invitation.estado == EstadoInvitacion.aceptada:
            return False  # No se puede revocar una invitación ya aceptada

        invitation.estado = EstadoInvitacion.expirada
        self.db.commit()
        return True

    def _is_group_admin(self, group_id: int, user_id: int) -> bool:
        """Verificar si un usuario es admin de un grupo"""
        usuario_grupo = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_grupo == group_id,
            UsuarioGrupo.id_usuario == user_id
        ).first()
        
        if not usuario_grupo:
            return False
        
        return usuario_grupo.rol == RolGrupo.admin

    def _is_user_in_group(self, group_id: int, user_id: int) -> bool:
        """Verificar si un usuario pertenece a un grupo"""
        return self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_grupo == group_id,
            UsuarioGrupo.id_usuario == user_id
        ).first() is not None

