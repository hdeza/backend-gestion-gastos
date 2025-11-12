# Paquete de modelos
from .user import Usuario, TipoUsuario
from .group import Grupo
from .expense import Gasto, MetodoPago
from .income import Ingreso
from .goal import Meta, EstadoMeta
from .category import Categoria, TipoCategoria
from .ai_history import HistorialAI, TipoHistorial
from .goal_contribution import AporteMeta
from .user_group import UsuarioGrupo, RolGrupo
from .invitation import Invitacion, EstadoInvitacion

# Exportar todas las clases para que estén disponibles
__all__ = [
    'Usuario', 'TipoUsuario',
    'Grupo',
    'Gasto', 'MetodoPago',
    'Ingreso',
    'Meta', 'EstadoMeta',
    'Categoria', 'TipoCategoria',
    'HistorialAI', 'TipoHistorial',
    'AporteMeta',
    'UsuarioGrupo', 'RolGrupo',
    'Invitacion', 'EstadoInvitacion'
]
