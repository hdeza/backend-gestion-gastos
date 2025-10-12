from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, DECIMAL, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

# Enums
class TipoUsuario(str, enum.Enum):
    normal = "normal"
    admin = "admin"

class TipoCategoria(str, enum.Enum):
    ingreso = "ingreso"
    gasto = "gasto"

class MetodoPago(str, enum.Enum):
    efectivo = "efectivo"
    tarjeta = "tarjeta"
    transferencia = "transferencia"
    otro = "otro"

class RolGrupo(str, enum.Enum):
    miembro = "miembro"
    admin = "admin"

class EstadoMeta(str, enum.Enum):
    activa = "activa"
    completada = "completada"
    cancelada = "cancelada"

class TipoHistorial(str, enum.Enum):
    recomendacion = "recomendacion"
    alerta = "alerta"
    analisis = "analisis"

# Modelo Usuarios
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False, index=True)
    contrasena_hash = Column(String(255), nullable=False)
    moneda_preferida = Column(String(10))
    fecha_registro = Column(DateTime, default=func.now())
    foto_perfil = Column(String(255))
    tipo_usuario = Column(Enum(TipoUsuario), default=TipoUsuario.normal)
    
    # Relaciones
    grupos_creados = relationship("Grupo", back_populates="creador")
    gastos = relationship("Gasto", back_populates="usuario")
    ingresos = relationship("Ingreso", back_populates="usuario")
    metas_personales = relationship("Meta", back_populates="usuario")
    categorias_personales = relationship("Categoria", back_populates="usuario")
    historial_ai = relationship("HistorialAI", back_populates="usuario")
    aportes_metas = relationship("AporteMeta", back_populates="usuario")
    usuarios_grupos = relationship("UsuarioGrupo", back_populates="usuario")

# Modelo Grupos
class Grupo(Base):
    __tablename__ = "grupos"
    
    id_grupo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_creacion = Column(DateTime, default=func.now())
    creado_por = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    
    # Relaciones
    creador = relationship("Usuario", back_populates="grupos_creados")
    gastos = relationship("Gasto", back_populates="grupo")
    ingresos = relationship("Ingreso", back_populates="grupo")
    metas_grupales = relationship("Meta", back_populates="grupo")
    usuarios_grupos = relationship("UsuarioGrupo", back_populates="grupo")

# Modelo Usuarios_Grupos
class UsuarioGrupo(Base):
    __tablename__ = "usuarios_grupos"
    
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), primary_key=True)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"), primary_key=True)
    rol = Column(Enum(RolGrupo), default=RolGrupo.miembro)
    fecha_union = Column(DateTime, default=func.now())
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="usuarios_grupos")
    grupo = relationship("Grupo", back_populates="usuarios_grupos")

# Modelo Categorias
class Categoria(Base):
    __tablename__ = "categorias"
    
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    tipo = Column(Enum(TipoCategoria))
    color = Column(String(20))
    icono = Column(String(100))
    es_global = Column(Boolean, default=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="categorias_personales")
    gastos = relationship("Gasto", back_populates="categoria")
    ingresos = relationship("Ingreso", back_populates="categoria")

# Modelo Gastos
class Gasto(Base):
    __tablename__ = "gastos"
    
    id_gasto = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    monto = Column(DECIMAL(12, 2), nullable=False)
    fecha = Column(Date, nullable=False)
    metodo_pago = Column(Enum(MetodoPago))
    nota = Column(Text)
    recurrente = Column(Boolean, default=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"))
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="gastos")
    usuario = relationship("Usuario", back_populates="gastos")
    grupo = relationship("Grupo", back_populates="gastos")

# Modelo Ingresos
class Ingreso(Base):
    __tablename__ = "ingresos"
    
    id_ingreso = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    monto = Column(DECIMAL(12, 2), nullable=False)
    fecha = Column(Date, nullable=False)
    fuente = Column(String(100))
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"))
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="ingresos")
    usuario = relationship("Usuario", back_populates="ingresos")
    grupo = relationship("Grupo", back_populates="ingresos")

# Modelo Metas
class Meta(Base):
    __tablename__ = "metas"
    
    id_meta = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    monto_objetivo = Column(DECIMAL(12, 2), nullable=False)
    monto_acumulado = Column(DECIMAL(12, 2), default=0)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    estado = Column(Enum(EstadoMeta))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"))
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="metas_personales")
    grupo = relationship("Grupo", back_populates="metas_grupales")
    aportes = relationship("AporteMeta", back_populates="meta")

# Modelo Aportes_Metas
class AporteMeta(Base):
    __tablename__ = "aportes_metas"
    
    id_aporte = Column(Integer, primary_key=True, index=True)
    id_meta = Column(Integer, ForeignKey("metas.id_meta"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    monto = Column(DECIMAL(12, 2), nullable=False)
    fecha = Column(Date, default=func.current_date())
    
    # Relaciones
    meta = relationship("Meta", back_populates="aportes")
    usuario = relationship("Usuario", back_populates="aportes_metas")

# Modelo Historial_AI
class HistorialAI(Base):
    __tablename__ = "historial_ai"
    
    id_historial = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    tipo = Column(Enum(TipoHistorial))
    contenido = Column(Text, nullable=False)
    fecha = Column(DateTime, default=func.now())
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="historial_ai")
