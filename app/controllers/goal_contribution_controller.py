"""
Controlador para gestión de aportes a metas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import Usuario
from app.schemas.goal_contribution import (
    AporteMetaResponse, AporteMetaCreate, AporteMetaUpdate, AporteMetaDetalleResponse
)
from app.services.goal_contribution_service import GoalContributionService
from app.controllers.auth_controller import get_current_user

router = APIRouter()

@router.post("/", response_model=AporteMetaResponse, status_code=status.HTTP_201_CREATED)
async def create_contribution(
    contribution: AporteMetaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo aporte a una meta
    """
    contribution_service = GoalContributionService(db)

    try:
        db_contribution = contribution_service.create_contribution(contribution, current_user.id_usuario)
        return db_contribution
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear aporte: {str(e)}"
        )

@router.get("/goal/{goal_id}", response_model=List[AporteMetaDetalleResponse])
async def get_contributions_by_goal(
    goal_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los aportes de una meta específica
    """
    contribution_service = GoalContributionService(db)
    contributions = contribution_service.get_contributions_by_goal(goal_id, current_user.id_usuario, skip, limit)
    
    # Enriquecer con nombres
    contributions_response = []
    for contrib in contributions:
        contributions_response.append(AporteMetaDetalleResponse(
            id_aporte=contrib.id_aporte,
            id_meta=contrib.id_meta,
            id_usuario=contrib.id_usuario,
            monto=contrib.monto,
            fecha=contrib.fecha,
            nombre_usuario=contrib.usuario.nombre if contrib.usuario else None,
            nombre_meta=contrib.meta.nombre if contrib.meta else None
        ))
    
    return contributions_response

@router.get("/user", response_model=List[AporteMetaResponse])
async def get_user_contributions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los aportes del usuario autenticado
    """
    contribution_service = GoalContributionService(db)
    contributions = contribution_service.get_contributions_by_user(current_user.id_usuario, skip, limit)
    return contributions

@router.get("/goal/{goal_id}/user/{user_id}", response_model=List[AporteMetaResponse])
async def get_user_contributions_by_goal(
    goal_id: int,
    user_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener aportes de un usuario específico a una meta
    """
    contribution_service = GoalContributionService(db)
    
    # Solo el mismo usuario o miembros del grupo pueden ver
    if user_id != current_user.id_usuario:
        from app.models.goal import Meta
        meta = db.query(Meta).filter(Meta.id_meta == goal_id).first()
        if meta and meta.id_grupo:
            from app.models.user_group import UsuarioGrupo
            user_in_group = db.query(UsuarioGrupo).filter(
                UsuarioGrupo.id_usuario == current_user.id_usuario,
                UsuarioGrupo.id_grupo == meta.id_grupo
            ).first()
            if not user_in_group:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes acceso a estos aportes"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a estos aportes"
            )
    
    contributions = contribution_service.get_user_contributions_by_goal(goal_id, user_id)
    return contributions

@router.get("/{contribution_id}", response_model=AporteMetaResponse)
async def get_contribution(
    contribution_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un aporte específico del usuario autenticado
    """
    contribution_service = GoalContributionService(db)
    contribution = contribution_service.get_contribution_by_id(contribution_id, current_user.id_usuario)

    if not contribution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aporte no encontrado"
        )

    return contribution

@router.put("/{contribution_id}", response_model=AporteMetaResponse)
async def update_contribution(
    contribution_id: int,
    contribution_update: AporteMetaUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un aporte del usuario autenticado
    """
    contribution_service = GoalContributionService(db)
    updated_contribution = contribution_service.update_contribution(
        contribution_id, contribution_update, current_user.id_usuario
    )

    if not updated_contribution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aporte no encontrado"
        )

    return updated_contribution

@router.delete("/{contribution_id}")
async def delete_contribution(
    contribution_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un aporte del usuario autenticado
    """
    contribution_service = GoalContributionService(db)
    success = contribution_service.delete_contribution(contribution_id, current_user.id_usuario)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aporte no encontrado"
        )

    return {"message": "Aporte eliminado exitosamente"}

@router.get("/goal/{goal_id}/total", response_model=dict)
async def get_total_contributions_by_goal(
    goal_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener el total de aportes de una meta
    """
    contribution_service = GoalContributionService(db)
    total = contribution_service.get_total_contributions_by_goal(goal_id, current_user.id_usuario)

    return {"total_aportes": total, "id_meta": goal_id}

