"""
Controlador para gestión de metas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.goal import Meta
from app.models.user import Usuario
from app.schemas.goal import MetaResponse, MetaCreate, MetaUpdate, MetaDetalleResponse
from app.services.goal_service import GoalService
from app.controllers.auth_controller import get_current_user

router = APIRouter()

@router.post("/", response_model=MetaResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal: MetaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear una nueva meta personal o grupal
    """
    goal_service = GoalService(db)

    # Si se especifica un grupo, verificar que el usuario pertenece a él
    if goal.id_grupo:
        from app.models.user_group import UsuarioGrupo
        user_in_group = db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == current_user.id_usuario,
            UsuarioGrupo.id_grupo == goal.id_grupo
        ).first()

        if not user_in_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No perteneces a este grupo"
            )

    try:
        db_goal = goal_service.create_goal(goal, current_user.id_usuario)
        return db_goal
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear meta: {str(e)}"
        )

@router.get("/", response_model=List[MetaResponse])
async def get_user_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    personal_only: bool = Query(False, description="Si es True, solo muestra metas personales (sin grupos)"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las metas del usuario autenticado.
    Si personal_only=True, solo muestra metas personales (sin grupos).
    """
    goal_service = GoalService(db)
    goals = goal_service.get_goals_by_user(current_user.id_usuario, skip, limit, personal_only)
    return goals

@router.get("/group/{group_id}", response_model=List[MetaResponse])
async def get_group_goals(
    group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener metas de un grupo específico
    """
    goal_service = GoalService(db)
    goals = goal_service.get_goals_by_group(group_id, current_user.id_usuario, skip, limit)
    return goals

@router.get("/{goal_id}", response_model=MetaDetalleResponse)
async def get_goal(
    goal_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener una meta específica con detalles de progreso
    """
    goal_service = GoalService(db)
    goal = goal_service.get_goal_by_id(goal_id, current_user.id_usuario)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta no encontrada"
        )

    # Obtener progreso
    progress = goal_service.get_goal_progress(goal_id, current_user.id_usuario)
    
    # Contar aportes
    from app.models.goal_contribution import AporteMeta
    total_aportes = db.query(AporteMeta).filter(AporteMeta.id_meta == goal_id).count()

    return MetaDetalleResponse(
        id_meta=goal.id_meta,
        nombre=goal.nombre,
        monto_objetivo=goal.monto_objetivo,
        monto_acumulado=goal.monto_acumulado,
        fecha_inicio=goal.fecha_inicio,
        fecha_fin=goal.fecha_fin,
        estado=goal.estado.value if goal.estado else None,
        id_usuario=goal.id_usuario,
        id_grupo=goal.id_grupo,
        porcentaje_completado=progress.get('porcentaje_completado') if progress else 0.0,
        total_aportes=total_aportes
    )

@router.put("/{goal_id}", response_model=MetaResponse)
async def update_goal(
    goal_id: int,
    goal_update: MetaUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar una meta del usuario autenticado
    """
    goal_service = GoalService(db)

    # Verificar que el grupo sea válido si se está actualizando
    if goal_update.id_grupo is not None:
        from app.models.user_group import UsuarioGrupo
        user_in_group = db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == current_user.id_usuario,
            UsuarioGrupo.id_grupo == goal_update.id_grupo
        ).first()

        if not user_in_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No perteneces a este grupo"
            )

    updated_goal = goal_service.update_goal(goal_id, goal_update, current_user.id_usuario)

    if not updated_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta no encontrada"
        )

    return updated_goal

@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar una meta del usuario autenticado
    """
    goal_service = GoalService(db)
    success = goal_service.delete_goal(goal_id, current_user.id_usuario)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta no encontrada"
        )

    return {"message": "Meta eliminada exitosamente"}

@router.get("/{goal_id}/progress", response_model=dict)
async def get_goal_progress(
    goal_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener progreso detallado de una meta
    """
    goal_service = GoalService(db)
    progress = goal_service.get_goal_progress(goal_id, current_user.id_usuario)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta no encontrada"
        )

    return progress

@router.get("/status/{estado}", response_model=List[MetaResponse])
async def get_goals_by_status(
    estado: str = Path(..., description="Estado de la meta: activa, completada, cancelada"),
    personal_only: bool = Query(False, description="Si es True, solo muestra metas personales"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener metas filtradas por estado
    """
    if estado not in ["activa", "completada", "cancelada"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Debe ser: activa, completada o cancelada"
        )

    goal_service = GoalService(db)
    goals = goal_service.get_goals_by_status(current_user.id_usuario, estado, personal_only)
    return goals

