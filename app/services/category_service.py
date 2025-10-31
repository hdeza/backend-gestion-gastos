"""
Servicio para gestión de categorías
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.category import Categoria, TipoCategoria
from app.schemas.category import CategoriaCreate, CategoriaUpdate


class CategoryService:
    """Servicio para operaciones de categorías"""

    def __init__(self, db: Session):
        self.db = db

    def create_category(self, category_data: CategoriaCreate, user_id: int) -> Categoria:
        """Crear nueva categoría"""
        # Si es global, verificar permisos (solo admin puede crear globales)
        if category_data.es_global:
            from app.models.user import Usuario, TipoUsuario
            user = self.db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
            if not user or user.tipo_usuario != TipoUsuario.admin:
                raise ValueError("Solo los administradores pueden crear categorías globales")

        db_category = Categoria(
            **category_data.dict(),
            id_usuario=user_id if not category_data.es_global else None
        )

        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def get_category_by_id(self, category_id: int, user_id: int = None) -> Optional[Categoria]:
        """Obtener categoría por ID"""
        category = self.db.query(Categoria).filter(Categoria.id_categoria == category_id).first()

        # Si es personal, verificar que pertenezca al usuario
        if category and not category.es_global and category.id_usuario != user_id:
            return None

        return category

    def get_categories_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Categoria]:
        """Obtener categorías disponibles para un usuario (personales + globales)"""
        return self.db.query(Categoria).filter(
            (Categoria.id_usuario == user_id) | (Categoria.es_global == True)
        ).offset(skip).limit(limit).all()

    def get_personal_categories_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Categoria]:
        """Obtener solo categorías personales de un usuario"""
        return self.db.query(Categoria).filter(
            Categoria.id_usuario == user_id,
            Categoria.es_global == False
        ).offset(skip).limit(limit).all()

    def get_global_categories(self, skip: int = 0, limit: int = 100) -> List[Categoria]:
        """Obtener todas las categorías globales"""
        return self.db.query(Categoria).filter(
            Categoria.es_global == True
        ).offset(skip).limit(limit).all()

    def get_categories_by_type(self, category_type: str, user_id: int, skip: int = 0, limit: int = 100) -> List[Categoria]:
        """Obtener categorías por tipo (ingreso/gasto) disponibles para el usuario"""
        return self.db.query(Categoria).filter(
            ((Categoria.id_usuario == user_id) | (Categoria.es_global == True)),
            Categoria.tipo == category_type
        ).offset(skip).limit(limit).all()

    def update_category(self, category_id: int, category_data: CategoriaUpdate, user_id: int) -> Optional[Categoria]:
        """Actualizar categoría (solo el propietario para categorías personales)"""
        category = self.get_category_by_id(category_id, user_id)

        if not category:
            return None

        # Solo el propietario puede actualizar categorías personales
        if not category.es_global and category.id_usuario != user_id:
            return None

        # Solo admin puede modificar categorías globales
        if category.es_global:
            from app.models.user import Usuario, TipoUsuario
            user = self.db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
            if not user or user.tipo_usuario != TipoUsuario.admin:
                raise ValueError("Solo los administradores pueden modificar categorías globales")

        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Eliminar categoría (solo el propietario para categorías personales)"""
        category = self.get_category_by_id(category_id, user_id)

        if not category:
            return False

        # Solo el propietario puede eliminar categorías personales
        if not category.es_global and category.id_usuario != user_id:
            return False

        # Solo admin puede eliminar categorías globales
        if category.es_global:
            from app.models.user import Usuario, TipoUsuario
            user = self.db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
            if not user or user.tipo_usuario != TipoUsuario.admin:
                raise ValueError("Solo los administradores pueden eliminar categorías globales")

        # Verificar que no esté siendo usada en gastos o ingresos
        gastos_count = self.db.query(Categoria).join(Categoria.gastos).filter(Categoria.id_categoria == category_id).count()
        ingresos_count = self.db.query(Categoria).join(Categoria.ingresos).filter(Categoria.id_categoria == category_id).count()

        if gastos_count > 0 or ingresos_count > 0:
            raise ValueError("No se puede eliminar una categoría que está siendo utilizada en gastos o ingresos")

        self.db.delete(category)
        self.db.commit()
        return True

    def get_category_usage_stats(self, category_id: int, user_id: int) -> dict:
        """Obtener estadísticas de uso de una categoría"""
        category = self.get_category_by_id(category_id, user_id)

        if not category:
            return None

        # Contar gastos e ingresos que usan esta categoría
        gastos_count = len(category.gastos) if category.gastos else 0
        ingresos_count = len(category.ingresos) if category.ingresos else 0

        # Calcular totales
        total_gastos = sum(gasto.monto for gasto in category.gastos) if category.gastos else 0
        total_ingresos = sum(ingreso.monto for ingreso in category.ingresos) if category.ingresos else 0

        return {
            "categoria": category.nombre,
            "tipo": category.tipo,
            "total_gastos": total_gastos,
            "total_ingresos": total_ingresos,
            "cantidad_gastos": gastos_count,
            "cantidad_ingresos": ingresos_count
        }
