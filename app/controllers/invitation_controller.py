"""
Controlador para gestión de invitaciones
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import Usuario
from app.schemas.invitation import (
    InvitacionResponse, InvitacionCreate, InvitacionDetalleResponse,
    AceptarInvitacionRequest, QRResponse
)
from app.services.invitation_service import InvitationService
from app.services.group_service import GroupService
from app.controllers.auth_controller import get_current_user
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token
from app.services.user_service import UserService

router = APIRouter()

# OAuth2 scheme para autenticación opcional
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[Usuario]:
    """Obtener usuario actual si está autenticado, None si no lo está"""
    if not token:
        return None
    try:
        from app.core.security import verify_token
        from app.services.user_service import UserService
        from fastapi import HTTPException, status
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        email = verify_token(token, credentials_exception)
        user_service = UserService(db)
        user = user_service.get_user_by_email(email)
        return user
    except:
        return None

@router.post("/", response_model=InvitacionResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    invitation: InvitacionCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear una nueva invitación para un grupo. Solo los administradores pueden crear invitaciones.
    """
    invitation_service = InvitationService(db)
    
    try:
        db_invitation = invitation_service.create_invitation(invitation, current_user.id_usuario)
        link = invitation_service.get_invitation_link(db_invitation.token)
        
        return InvitacionResponse(
            id_invitacion=db_invitation.id_invitacion,
            id_grupo=db_invitation.id_grupo,
            token=db_invitation.token,
            link_invitacion=link,
            estado=db_invitation.estado.value,
            fecha_creacion=db_invitation.fecha_creacion,
            fecha_expiracion=db_invitation.fecha_expiracion,
            creado_por=db_invitation.creado_por,
            id_usuario_invitado=db_invitation.id_usuario_invitado
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear invitación: {str(e)}"
        )

@router.get("/group/{group_id}", response_model=List[InvitacionResponse])
async def get_group_invitations(
    group_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las invitaciones de un grupo (solo administradores)
    """
    invitation_service = InvitationService(db)
    invitations = invitation_service.get_group_invitations(group_id, current_user.id_usuario)
    
    if invitations is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver las invitaciones de este grupo"
        )

    invitations_response = []
    for inv in invitations:
        link = invitation_service.get_invitation_link(inv.token)
        invitations_response.append(InvitacionResponse(
            id_invitacion=inv.id_invitacion,
            id_grupo=inv.id_grupo,
            token=inv.token,
            link_invitacion=link,
            estado=inv.estado.value,
            fecha_creacion=inv.fecha_creacion,
            fecha_expiracion=inv.fecha_expiracion,
            creado_por=inv.creado_por,
            id_usuario_invitado=inv.id_usuario_invitado
        ))

    return invitations_response

@router.get("/token/{token}", response_model=InvitacionDetalleResponse)
async def get_invitation_by_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Obtener detalles de una invitación por token. 
    Este endpoint puede ser accedido sin autenticación para ver la invitación.
    """
    invitation_service = InvitationService(db)
    invitation = invitation_service.get_invitation_by_token(token)
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitación no encontrada o expirada"
        )

    group = invitation.grupo
    creador = invitation.creador
    
    link = invitation_service.get_invitation_link(token)
    
    return InvitacionDetalleResponse(
        id_invitacion=invitation.id_invitacion,
        id_grupo=invitation.id_grupo,
        token=invitation.token,
        link_invitacion=link,
        estado=invitation.estado.value,
        fecha_creacion=invitation.fecha_creacion,
        fecha_expiracion=invitation.fecha_expiracion,
        creado_por=invitation.creado_por,
        id_usuario_invitado=invitation.id_usuario_invitado,
        grupo_nombre=group.nombre if group else None,
        grupo_descripcion=group.descripcion if group else None,
        creador_nombre=creador.nombre if creador else None
    )

@router.get("/{invitation_id}/qr", response_model=QRResponse)
async def get_invitation_qr(
    invitation_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generar código QR para una invitación (solo administradores del grupo)
    """
    from app.models.invitation import Invitacion
    
    invitation = db.query(Invitacion).filter(
        Invitacion.id_invitacion == invitation_id
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitación no encontrada"
        )

    invitation_service = InvitationService(db)
    
    # Verificar permisos
    if not invitation_service._is_group_admin(invitation.id_grupo, current_user.id_usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para generar QR de esta invitación"
        )

    qr_base64 = invitation_service.generate_qr_code(invitation.token)
    link = invitation_service.get_invitation_link(invitation.token)

    if not qr_base64:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo generar el código QR. Asegúrate de tener instalada la librería 'qrcode'."
        )

    return QRResponse(
        qr_code_base64=qr_base64,
        link_invitacion=link,
        token=invitation.token
    )

@router.post("/accept", response_model=dict)
async def accept_invitation(
    request: AceptarInvitacionRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aceptar una invitación y unirse al grupo
    """
    invitation_service = InvitationService(db)
    success = invitation_service.accept_invitation(request.token, current_user.id_usuario)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo aceptar la invitación. Verifica que el token sea válido y que no estés ya en el grupo."
        )

    return {"message": "Invitación aceptada exitosamente. Te has unido al grupo."}

@router.post("/reject", response_model=dict)
async def reject_invitation(
    request: AceptarInvitacionRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rechazar una invitación
    """
    invitation_service = InvitationService(db)
    success = invitation_service.reject_invitation(request.token, current_user.id_usuario)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo rechazar la invitación. Verifica que el token sea válido."
        )

    return {"message": "Invitación rechazada exitosamente"}

@router.delete("/{invitation_id}")
async def revoke_invitation(
    invitation_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revocar una invitación (solo administradores del grupo)
    """
    from app.models.invitation import Invitacion
    
    invitation = db.query(Invitacion).filter(
        Invitacion.id_invitacion == invitation_id
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitación no encontrada"
        )

    invitation_service = InvitationService(db)
    success = invitation_service.revoke_invitation(
        invitation_id, 
        invitation.id_grupo, 
        current_user.id_usuario
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo revocar la invitación. Verifica que tengas permisos de administrador."
        )

    return {"message": "Invitación revocada exitosamente"}

