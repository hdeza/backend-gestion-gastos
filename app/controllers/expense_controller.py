"""
Controlador para gestión de gastos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.expense import Gasto
from app.models.user import Usuario
from app.schemas.expense import GastoResponse, GastoCreate, GastoUpdate
from app.services.expense_service import ExpenseService
from app.controllers.auth_controller import get_current_user

router = APIRouter()

@router.post("/", response_model=GastoResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: GastoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo gasto para el usuario autenticado
    """
    expense_service = ExpenseService(db)

    # Si se especifica un grupo, verificar que el usuario pertenece a él
    if expense.id_grupo:
        from app.models.user_group import UsuarioGrupo
        user_in_group = db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == current_user.id_usuario,
            UsuarioGrupo.id_grupo == expense.id_grupo
        ).first()

        if not user_in_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No perteneces a este grupo"
            )

    try:
        db_expense = expense_service.create_expense(expense, current_user.id_usuario)
        return db_expense
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear gasto: {str(e)}"
        )

@router.get("/", response_model=List[GastoResponse])
async def get_user_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    personal_only: bool = Query(False, description="Si es True, solo muestra gastos personales (sin grupos)"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los gastos del usuario autenticado.
    Si personal_only=True, solo muestra gastos personales (sin grupos).
    """
    expense_service = ExpenseService(db)
    expenses = expense_service.get_expenses_by_user(current_user.id_usuario, skip, limit, personal_only)
    return expenses

@router.get("/group/{group_id}", response_model=List[GastoResponse])
async def get_group_expenses(
    group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener gastos de un grupo específico
    """
    expense_service = ExpenseService(db)
    expenses = expense_service.get_expenses_by_group(group_id, current_user.id_usuario, skip, limit)
    return expenses

@router.get("/{expense_id}", response_model=GastoResponse)
async def get_expense(
    expense_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un gasto específico del usuario autenticado
    """
    expense_service = ExpenseService(db)
    expense = expense_service.get_expense_by_id(expense_id, current_user.id_usuario)

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )

    return expense

@router.put("/{expense_id}", response_model=GastoResponse)
async def update_expense(
    expense_id: int,
    expense_update: GastoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un gasto del usuario autenticado
    """
    expense_service = ExpenseService(db)

    # Verificar que el grupo sea válido si se está actualizando
    if expense_update.id_grupo:
        from app.models.user_group import UsuarioGrupo
        user_in_group = db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == current_user.id_usuario,
            UsuarioGrupo.id_grupo == expense_update.id_grupo
        ).first()

        if not user_in_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No perteneces a este grupo"
            )

    updated_expense = expense_service.update_expense(expense_id, expense_update, current_user.id_usuario)

    if not updated_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )

    return updated_expense

@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un gasto del usuario autenticado
    """
    expense_service = ExpenseService(db)
    success = expense_service.delete_expense(expense_id, current_user.id_usuario)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )

    return {"message": "Gasto eliminado exitosamente"}

@router.get("/total/amount", response_model=dict)
async def get_total_expense(
    personal_only: bool = Query(False, description="Si es True, solo cuenta gastos personales"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener el total de gastos del usuario autenticado.
    Si personal_only=True, solo cuenta gastos personales (sin grupos).
    """
    expense_service = ExpenseService(db)
    total = expense_service.get_total_expense_by_user(current_user.id_usuario, personal_only)

    return {"total_gastos": total}

@router.get("/group/{group_id}/total/amount", response_model=dict)
async def get_total_group_expense(
    group_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener el total de gastos de un grupo específico
    """
    expense_service = ExpenseService(db)
    
    # Verificar que el usuario pertenece al grupo
    from app.models.user_group import UsuarioGrupo
    user_in_group = db.query(UsuarioGrupo).filter(
        UsuarioGrupo.id_usuario == current_user.id_usuario,
        UsuarioGrupo.id_grupo == group_id
    ).first()
    
    if not user_in_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No perteneces a este grupo"
        )
    
    total = expense_service.get_total_expense_by_group(group_id, current_user.id_usuario)
    return {"total_gastos": total, "id_grupo": group_id}

@router.get("/date-range/", response_model=List[GastoResponse])
async def get_expenses_by_date_range(
    start_date: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    personal_only: bool = Query(False, description="Si es True, solo muestra gastos personales"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener gastos por rango de fechas.
    Si personal_only=True, solo muestra gastos personales (sin grupos).
    """
    try:
        # Validar formato de fechas
        from datetime import datetime
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')

        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )

    expense_service = ExpenseService(db)
    expenses = expense_service.get_expense_by_date_range(current_user.id_usuario, start_date, end_date, personal_only)

    return expenses

@router.get("/group/{group_id}/date-range/", response_model=List[GastoResponse])
async def get_group_expenses_by_date_range(
    group_id: int,
    start_date: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener gastos de un grupo por rango de fechas
    """
    try:
        # Validar formato de fechas
        from datetime import datetime
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')

        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )

    expense_service = ExpenseService(db)
    
    # Verificar que el usuario pertenece al grupo
    from app.models.user_group import UsuarioGrupo
    user_in_group = db.query(UsuarioGrupo).filter(
        UsuarioGrupo.id_usuario == current_user.id_usuario,
        UsuarioGrupo.id_grupo == group_id
    ).first()
    
    if not user_in_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No perteneces a este grupo"
        )
    
    expenses = expense_service.get_group_expense_by_date_range(group_id, current_user.id_usuario, start_date, end_date)
    return expenses

@router.get("/category/{category_id}", response_model=List[GastoResponse])
async def get_expenses_by_category(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    personal_only: bool = Query(False, description="Si es True, solo muestra gastos personales"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener gastos por categoría específica.
    Si personal_only=True, solo muestra gastos personales (sin grupos).
    """
    expense_service = ExpenseService(db)
    expenses = expense_service.get_expenses_by_category(current_user.id_usuario, category_id, skip, limit, personal_only)
    return expenses

@router.get("/group/{group_id}/category/{category_id}", response_model=List[GastoResponse])
async def get_group_expenses_by_category(
    group_id: int,
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener gastos de un grupo por categoría específica
    """
    expense_service = ExpenseService(db)
    
    # Verificar que el usuario pertenece al grupo
    from app.models.user_group import UsuarioGrupo
    user_in_group = db.query(UsuarioGrupo).filter(
        UsuarioGrupo.id_usuario == current_user.id_usuario,
        UsuarioGrupo.id_grupo == group_id
    ).first()
    
    if not user_in_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No perteneces a este grupo"
        )
    
    expenses = expense_service.get_group_expenses_by_category(group_id, current_user.id_usuario, category_id, skip, limit)
    return expenses

