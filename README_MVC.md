# 🏦 API de Gestión de Gastos - Arquitectura MVC

## 📋 Descripción

API REST desarrollada con **FastAPI** siguiendo la arquitectura **Modelo-Vista-Controlador (MVC)** para un sistema de gestión financiera inteligente orientado a estudiantes universitarios.

## 🏗️ Arquitectura MVC

### **Estructura del Proyecto**

```
backend-gestion-gastos/
├── app/                          # Paquete principal de la aplicación
│   ├── __init__.py
│   ├── main.py                  # Aplicación FastAPI principal
│   │
│   ├── core/                    # Configuración central
│   │   ├── __init__.py
│   │   ├── config.py            # Configuración de la aplicación
│   │   ├── database.py          # Configuración de base de datos
│   │   └── security.py          # Utilidades de seguridad
│   │
│   ├── models/                  # MODELOS (Capa de datos)
│   │   ├── __init__.py
│   │   ├── user.py              # Modelo Usuario
│   │   ├── group.py             # Modelo Grupo
│   │   ├── category.py          # Modelo Categoría
│   │   ├── expense.py           # Modelo Gasto
│   │   ├── income.py            # Modelo Ingreso
│   │   ├── goal.py              # Modelo Meta
│   │   ├── user_group.py        # Modelo UsuarioGrupo
│   │   ├── goal_contribution.py # Modelo AporteMeta
│   │   └── ai_history.py       # Modelo HistorialAI
│   │
│   ├── schemas/                 # ESQUEMAS (Validación de datos)
│   │   ├── __init__.py
│   │   ├── user.py              # Esquemas de Usuario
│   │   ├── auth.py              # Esquemas de Autenticación
│   │   ├── category.py          # Esquemas de Categoría
│   │   ├── expense.py          # Esquemas de Gasto
│   │   └── income.py            # Esquemas de Ingreso
│   │
│   ├── services/                # SERVICIOS (Lógica de negocio)
│   │   ├── __init__.py
│   │   ├── user_service.py      # Servicio de usuarios
│   │   └── auth_service.py     # Servicio de autenticación
│   │
│   └── controllers/              # CONTROLADORES (Endpoints API)
│       ├── __init__.py
│       ├── auth_controller.py   # Controlador de autenticación
│       └── user_controller.py   # Controlador de usuarios
│
├── main.py                      # Punto de entrada de la aplicación
├── requirements.txt             # Dependencias Python
├── Dockerfile                   # Imagen Docker
├── docker-compose.yml           # Orquestación de servicios
├── bd.sql                      # Script de inicialización BD
└── README.md                   # Documentación
```

## 🎯 **Separación de Responsabilidades**

### **📊 MODELOS (app/models/)**

- **Responsabilidad**: Representación de datos y relaciones
- **Tecnología**: SQLAlchemy ORM
- **Contenido**: Clases que mapean las tablas de la base de datos
- **Ejemplo**: `Usuario`, `Gasto`, `Ingreso`, `Categoria`

### **🔧 SERVICIOS (app/services/)**

- **Responsabilidad**: Lógica de negocio y operaciones complejas
- **Tecnología**: Clases Python puras
- **Contenido**: Métodos para crear, leer, actualizar y eliminar datos
- **Ejemplo**: `UserService`, `AuthService`

### **🎮 CONTROLADORES (app/controllers/)**

- **Responsabilidad**: Manejo de requests HTTP y respuestas
- **Tecnología**: FastAPI routers
- **Contenido**: Endpoints de la API REST
- **Ejemplo**: `auth_controller`, `user_controller`

### **📋 ESQUEMAS (app/schemas/)**

- **Responsabilidad**: Validación y serialización de datos
- **Tecnología**: Pydantic models
- **Contenido**: Estructuras de datos para requests/responses
- **Ejemplo**: `UsuarioCreate`, `UsuarioResponse`, `Token`

### **⚙️ CONFIGURACIÓN (app/core/)**

- **Responsabilidad**: Configuración central y utilidades
- **Tecnología**: Python modules
- **Contenido**: Configuración, base de datos, seguridad
- **Ejemplo**: `config.py`, `database.py`, `security.py`

## 🚀 **Ventajas de la Arquitectura MVC**

### **✅ Separación Clara de Responsabilidades**

- **Modelos**: Solo manejan datos
- **Servicios**: Solo lógica de negocio
- **Controladores**: Solo manejo de HTTP

### **✅ Escalabilidad**

- Fácil agregar nuevos controladores
- Servicios reutilizables
- Modelos independientes

### **✅ Mantenibilidad**

- Código organizado y modular
- Fácil localizar funcionalidades
- Testing independiente por capas

### **✅ Reutilización**

- Servicios pueden ser usados por múltiples controladores
- Modelos consistentes en toda la aplicación
- Esquemas compartidos

## 🔄 **Flujo de Datos MVC**

```
1. REQUEST → Controlador
2. Controlador → Servicio
3. Servicio → Modelo
4. Modelo → Base de Datos
5. Base de Datos → Modelo
6. Modelo → Servicio
7. Servicio → Controlador
8. Controlador → RESPONSE
```

## 📚 **Ejemplo de Implementación**

### **Modelo (app/models/user.py)**

```python
class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    # ... más campos
```

### **Servicio (app/services/user_service.py)**

```python
class UserService:
    def create_user(self, user_data: UsuarioCreate) -> Usuario:
        # Lógica de negocio para crear usuario
        pass
```

### **Controlador (app/controllers/auth_controller.py)**

```python
@router.post("/register")
async def register_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    # Manejo del endpoint HTTP
    pass
```

### **Esquema (app/schemas/user.py)**

```python
class UsuarioCreate(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str
```

## 🎯 **Endpoints Implementados**

### **Autenticación**

- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Inicio de sesión
- `GET /api/auth/me` - Perfil del usuario
- `GET /api/auth/verify-token` - Verificar token
- `POST /api/auth/change-password` - Cambiar contraseña

### **Usuarios**

- `GET /api/users/profile` - Obtener perfil
- `PUT /api/users/profile` - Actualizar perfil

## 🚀 **Cómo Ejecutar**

### **Con Docker (Recomendado)**

```bash
docker-compose up -d
```

### **Localmente**

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

## 🔧 **Configuración**

La configuración se centraliza en `app/core/config.py`:

- Variables de entorno
- Configuración de base de datos
- Configuración JWT
- Configuración CORS

## 📈 **Escalabilidad Futura**

### **Agregar Nuevos Controladores**

1. Crear archivo en `app/controllers/`
2. Implementar endpoints
3. Agregar al `app/main.py`

### **Agregar Nuevos Servicios**

1. Crear archivo en `app/services/`
2. Implementar lógica de negocio
3. Usar en controladores

### **Agregar Nuevos Modelos**

1. Crear archivo en `app/models/`
2. Definir tabla y relaciones
3. Crear esquemas correspondientes

---

**¡Arquitectura MVC implementada exitosamente! 🎉**

La separación de responsabilidades permite un desarrollo más organizado, mantenible y escalable.
