"""
Servicio para gestión de gastos
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.expense import Gasto
from app.schemas.expense import GastoCreate, GastoUpdate


class ExpenseService:
    """Servicio para operaciones de gastos"""

    def __init__(self, db: Session):
        self.db = db

    def create_expense(self, expense_data: GastoCreate, user_id: int) -> Gasto:
        """Crear nuevo gasto"""
        db_expense = Gasto(
            **expense_data.dict(),
            id_usuario=user_id
        )

        self.db.add(db_expense)
        self.db.commit()
        self.db.refresh(db_expense)
        return db_expense

    def get_expense_by_id(self, expense_id: int, user_id: int) -> Optional[Gasto]:
        """Obtener gasto por ID (del usuario o de un grupo al que pertenece)"""
        expense = self.db.query(Gasto).filter(
            Gasto.id_gasto == expense_id
        ).first()
        
        if not expense:
            return None
        
        # Si es gasto personal del usuario
        if expense.id_usuario == user_id and not expense.id_grupo:
            return expense
        
        # Si es gasto de grupo, verificar que el usuario pertenece al grupo
        if expense.id_grupo:
            from app.models.user_group import UsuarioGrupo
            user_in_group = self.db.query(UsuarioGrupo).filter(
                UsuarioGrupo.id_usuario == user_id,
                UsuarioGrupo.id_grupo == expense.id_grupo
            ).first()
            if user_in_group:
                return expense
        
        return None

    def get_expenses_by_user(self, user_id: int, skip: int = 0, limit: int = 100, personal_only: bool = False) -> List[Gasto]:
        """Obtener todos los gastos de un usuario (personales o todos incluyendo grupos)"""
        query = self.db.query(Gasto).filter(
            Gasto.id_usuario == user_id
        )
        
        if personal_only:
            query = query.filter(Gasto.id_grupo.is_(None))
        
        return query.offset(skip).limit(limit).all()

    def get_expenses_by_group(self, group_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[Gasto]:
        """Obtener gastos de un grupo (solo si el usuario pertenece al grupo)"""
        # Primero verificar que el usuario pertenece al grupo
        from app.models.user_group import UsuarioGrupo
        user_in_group = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == user_id,
            UsuarioGrupo.id_grupo == group_id
        ).first()

        if not user_in_group:
            return []

        return self.db.query(Gasto).filter(
            Gasto.id_grupo == group_id
        ).offset(skip).limit(limit).all()

    def get_all_expenses(self, skip: int = 0, limit: int = 100) -> List[Gasto]:
        """Obtener todos los gastos (para administradores)"""
        return self.db.query(Gasto).offset(skip).limit(limit).all()

    def update_expense(self, expense_id: int, expense_data: GastoUpdate, user_id: int) -> Optional[Gasto]:
        """Actualizar gasto (del usuario o de un grupo al que pertenece)"""
        expense = self.get_expense_by_id(expense_id, user_id)
        if not expense:
            return None

        # Verificar que el grupo sea válido si se está actualizando
        if expense_data.id_grupo is not None:
            from app.models.user_group import UsuarioGrupo
            user_in_group = self.db.query(UsuarioGrupo).filter(
                UsuarioGrupo.id_usuario == user_id,
                UsuarioGrupo.id_grupo == expense_data.id_grupo
            ).first()
            if not user_in_group:
                return None

        update_data = expense_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)

        self.db.commit()
        self.db.refresh(expense)
        return expense

    def delete_expense(self, expense_id: int, user_id: int) -> bool:
        """Eliminar gasto (solo del usuario autenticado)"""
        expense = self.get_expense_by_id(expense_id, user_id)
        if not expense:
            return False

        self.db.delete(expense)
        self.db.commit()
        return True

    def get_total_expense_by_user(self, user_id: int, personal_only: bool = False) -> float:
        """Obtener el total de gastos de un usuario (personales o todos)"""
        from sqlalchemy import func
        query = self.db.query(func.sum(Gasto.monto)).filter(
            Gasto.id_usuario == user_id
        )
        
        if personal_only:
            query = query.filter(Gasto.id_grupo.is_(None))
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    def get_total_expense_by_group(self, group_id: int, user_id: int) -> float:
        """Obtener el total de gastos de un grupo (solo si el usuario pertenece)"""
        from sqlalchemy import func
        from app.models.user_group import UsuarioGrupo
        
        # Verificar que el usuario pertenece al grupo
        user_in_group = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == user_id,
            UsuarioGrupo.id_grupo == group_id
        ).first()
        
        if not user_in_group:
            return 0.0
        
        result = self.db.query(func.sum(Gasto.monto)).filter(
            Gasto.id_grupo == group_id
        ).scalar()
        
        return float(result) if result else 0.0

    def get_expense_by_date_range(self, user_id: int, start_date: str, end_date: str, personal_only: bool = False) -> List[Gasto]:
        """Obtener gastos por rango de fechas (personales o todos)"""
        from sqlalchemy import and_
        query = self.db.query(Gasto).filter(
            and_(
                Gasto.id_usuario == user_id,
                Gasto.fecha >= start_date,
                Gasto.fecha <= end_date
            )
        )
        
        if personal_only:
            query = query.filter(Gasto.id_grupo.is_(None))
        
        return query.all()
    
    def get_group_expense_by_date_range(self, group_id: int, user_id: int, start_date: str, end_date: str) -> List[Gasto]:
        """Obtener gastos de grupo por rango de fechas"""
        from sqlalchemy import and_
        from app.models.user_group import UsuarioGrupo
        
        # Verificar que el usuario pertenece al grupo
        user_in_group = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == user_id,
            UsuarioGrupo.id_grupo == group_id
        ).first()
        
        if not user_in_group:
            return []
        
        return self.db.query(Gasto).filter(
            and_(
                Gasto.id_grupo == group_id,
                Gasto.fecha >= start_date,
                Gasto.fecha <= end_date
            )
        ).all()

    def get_expenses_by_category(self, user_id: int, category_id: int, skip: int = 0, limit: int = 100, personal_only: bool = False) -> List[Gasto]:
        """Obtener gastos por categoría (personales o todos)"""
        query = self.db.query(Gasto).filter(
            Gasto.id_usuario == user_id,
            Gasto.id_categoria == category_id
        )
        
        if personal_only:
            query = query.filter(Gasto.id_grupo.is_(None))
        
        return query.offset(skip).limit(limit).all()
    
    def get_group_expenses_by_category(self, group_id: int, user_id: int, category_id: int, skip: int = 0, limit: int = 100) -> List[Gasto]:
        """Obtener gastos de grupo por categoría"""
        from app.models.user_group import UsuarioGrupo
        
        # Verificar que el usuario pertenece al grupo
        user_in_group = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == user_id,
            UsuarioGrupo.id_grupo == group_id
        ).first()
        
        if not user_in_group:
            return []
        
        return self.db.query(Gasto).filter(
            Gasto.id_grupo == group_id,
            Gasto.id_categoria == category_id
        ).offset(skip).limit(limit).all()

