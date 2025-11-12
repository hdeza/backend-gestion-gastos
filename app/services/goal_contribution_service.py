"""
Servicio para gestión de aportes a metas
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.goal_contribution import AporteMeta
from app.models.goal import Meta
from app.schemas.goal_contribution import AporteMetaCreate, AporteMetaUpdate
from decimal import Decimal


class GoalContributionService:
    """Servicio para operaciones de aportes a metas"""

    def __init__(self, db: Session):
        self.db = db

    def create_contribution(self, contribution_data: AporteMetaCreate, user_id: int) -> AporteMeta:
        """Crear nuevo aporte a una meta"""
        # Verificar que la meta existe y el usuario tiene acceso
        meta = self.db.query(Meta).filter(Meta.id_meta == contribution_data.id_meta).first()
        if not meta:
            raise ValueError("Meta no encontrada")
        
        # Verificar acceso a la meta
        if meta.id_usuario != user_id:
            if meta.id_grupo:
                from app.models.user_group import UsuarioGrupo
                user_in_group = self.db.query(UsuarioGrupo).filter(
                    UsuarioGrupo.id_usuario == user_id,
                    UsuarioGrupo.id_grupo == meta.id_grupo
                ).first()
                if not user_in_group:
                    raise ValueError("No tienes acceso a esta meta")
            else:
                raise ValueError("No tienes acceso a esta meta")
        
        # Verificar que la meta esté activa
        if meta.estado.value != "activa":
            raise ValueError("Solo se pueden hacer aportes a metas activas")
        
        db_contribution = AporteMeta(
            id_meta=contribution_data.id_meta,
            id_usuario=user_id,
            monto=contribution_data.monto,
            fecha=contribution_data.fecha
        )

        self.db.add(db_contribution)
        self.db.commit()
        self.db.refresh(db_contribution)
        
        # Actualizar monto acumulado de la meta
        self._update_goal_accumulated(contribution_data.id_meta)
        
        return db_contribution

    def _update_goal_accumulated(self, goal_id: int):
        """Actualizar monto acumulado de una meta"""
        from sqlalchemy import func
        
        total_aportes = self.db.query(func.sum(AporteMeta.monto)).filter(
            AporteMeta.id_meta == goal_id
        ).scalar()
        
        meta = self.db.query(Meta).filter(Meta.id_meta == goal_id).first()
        if meta:
            monto_acumulado = Decimal(str(total_aportes)) if total_aportes else Decimal('0.00')
            meta.monto_acumulado = monto_acumulado
            
            # Verificar si se completó
            from app.models.goal import EstadoMeta
            if monto_acumulado >= meta.monto_objetivo and meta.estado == EstadoMeta.activa:
                meta.estado = EstadoMeta.completada
            
            self.db.commit()
            self.db.refresh(meta)

    def get_contribution_by_id(self, contribution_id: int, user_id: int) -> Optional[AporteMeta]:
        """Obtener aporte por ID (solo del usuario autenticado)"""
        contribution = self.db.query(AporteMeta).filter(
            AporteMeta.id_aporte == contribution_id,
            AporteMeta.id_usuario == user_id
        ).first()
        return contribution

    def get_contributions_by_goal(self, goal_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[AporteMeta]:
        """Obtener todos los aportes de una meta (solo si el usuario tiene acceso)"""
        # Verificar acceso a la meta
        meta = self.db.query(Meta).filter(Meta.id_meta == goal_id).first()
        if not meta:
            return []
        
        if meta.id_usuario != user_id:
            if meta.id_grupo:
                from app.models.user_group import UsuarioGrupo
                user_in_group = self.db.query(UsuarioGrupo).filter(
                    UsuarioGrupo.id_usuario == user_id,
                    UsuarioGrupo.id_grupo == meta.id_grupo
                ).first()
                if not user_in_group:
                    return []
            else:
                return []
        
        return self.db.query(AporteMeta).filter(
            AporteMeta.id_meta == goal_id
        ).offset(skip).limit(limit).all()

    def get_contributions_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[AporteMeta]:
        """Obtener todos los aportes de un usuario"""
        return self.db.query(AporteMeta).filter(
            AporteMeta.id_usuario == user_id
        ).offset(skip).limit(limit).all()

    def update_contribution(self, contribution_id: int, contribution_data: AporteMetaUpdate, user_id: int) -> Optional[AporteMeta]:
        """Actualizar aporte (solo del usuario autenticado)"""
        contribution = self.get_contribution_by_id(contribution_id, user_id)
        if not contribution:
            return None

        update_data = contribution_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contribution, field, value)

        self.db.commit()
        self.db.refresh(contribution)
        
        # Actualizar monto acumulado de la meta
        self._update_goal_accumulated(contribution.id_meta)
        
        return contribution

    def delete_contribution(self, contribution_id: int, user_id: int) -> bool:
        """Eliminar aporte (solo del usuario autenticado)"""
        contribution = self.get_contribution_by_id(contribution_id, user_id)
        if not contribution:
            return False

        goal_id = contribution.id_meta
        self.db.delete(contribution)
        self.db.commit()
        
        # Actualizar monto acumulado de la meta
        self._update_goal_accumulated(goal_id)
        
        return True

    def get_total_contributions_by_goal(self, goal_id: int, user_id: int) -> float:
        """Obtener el total de aportes de una meta"""
        # Verificar acceso
        meta = self.db.query(Meta).filter(Meta.id_meta == goal_id).first()
        if not meta:
            return 0.0
        
        if meta.id_usuario != user_id:
            if meta.id_grupo:
                from app.models.user_group import UsuarioGrupo
                user_in_group = self.db.query(UsuarioGrupo).filter(
                    UsuarioGrupo.id_usuario == user_id,
                    UsuarioGrupo.id_grupo == meta.id_grupo
                ).first()
                if not user_in_group:
                    return 0.0
            else:
                return 0.0
        
        from sqlalchemy import func
        result = self.db.query(func.sum(AporteMeta.monto)).filter(
            AporteMeta.id_meta == goal_id
        ).scalar()

        return float(result) if result else 0.0

    def get_user_contributions_by_goal(self, goal_id: int, user_id: int) -> List[AporteMeta]:
        """Obtener aportes de un usuario específico a una meta"""
        # Verificar acceso a la meta
        meta = self.db.query(Meta).filter(Meta.id_meta == goal_id).first()
        if not meta:
            return []
        
        if meta.id_usuario != user_id:
            if meta.id_grupo:
                from app.models.user_group import UsuarioGrupo
                user_in_group = self.db.query(UsuarioGrupo).filter(
                    UsuarioGrupo.id_usuario == user_id,
                    UsuarioGrupo.id_grupo == meta.id_grupo
                ).first()
                if not user_in_group:
                    return []
            else:
                return []
        
        return self.db.query(AporteMeta).filter(
            AporteMeta.id_meta == goal_id,
            AporteMeta.id_usuario == user_id
        ).all()

