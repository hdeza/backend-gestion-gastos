# 🏦 API de Gestión de Gastos - Sistema para Estudiantes Universitarios

## 📋 Descripción

API REST desarrollada con FastAPI para un sistema de gestión financiera inteligente orientado a estudiantes universitarios. Permite gestionar gastos personales y grupales, categorías compartidas, metas financieras y análisis con IA.

## 🚀 Características

- ✅ **Autenticación JWT** - Sistema seguro de login y registro
- ✅ **Gestión de Usuarios** - Perfiles personalizados con moneda preferida
- ✅ **Grupos Colaborativos** - Gastos e ingresos compartidos
- ✅ **Categorías Inteligentes** - Globales y personalizadas
- ✅ **Metas Financieras** - Personales y grupales con seguimiento
- ✅ **Dockerizado** - Fácil despliegue con PostgreSQL
- ✅ **Documentación Automática** - Swagger UI integrado

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional robusta
- **SQLAlchemy** - ORM para Python
- **JWT** - Autenticación segura
- **Docker** - Containerización
- **Pydantic** - Validación de datos

## 📁 Estructura del Proyecto

```
backend-gestion-gastos/
├── main.py                 # Aplicación principal FastAPI
├── database.py            # Configuración de base de datos
├── models.py              # Modelos SQLAlchemy
├── schemas.py             # Esquemas Pydantic
├── auth.py                # Utilidades de autenticación
├── routers/
│   └── auth.py           # Endpoints de autenticación
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Imagen Docker
├── docker-compose.yml    # Orquestación de servicios
├── bd.sql               # Script de inicialización BD
└── README.md            # Documentación
```

## 🚀 Instalación y Uso

### Opción 1: Docker (Recomendado)

1. **Clonar el repositorio**

```bash
git clone <tu-repositorio>
cd backend-gestion-gastos
```

2. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Ejecutar con Docker Compose**

```bash
docker-compose up -d
```

4. **Acceder a la API**

- API: http://localhost:8000
- Documentación: http://localhost:8000/docs
- Base de datos: localhost:5432

### Opción 2: Instalación Local

1. **Crear entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

2. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

3. **Configurar PostgreSQL**

```bash
# Crear base de datos
createdb gestion_gastos

# Ejecutar script de inicialización
psql -d gestion_gastos -f bd.sql
```

4. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar aplicación**

```bash
uvicorn main:app --reload
```

## 🔐 Endpoints de Autenticación

### POST `/api/auth/register`

Registrar nuevo usuario

```json
{
  "nombre": "Juan Pérez",
  "correo": "juan@ejemplo.com",
  "contrasena": "mi_password_seguro",
  "moneda_preferida": "COP"
}
```

### POST `/api/auth/login`

Iniciar sesión

```json
{
  "username": "juan@ejemplo.com",
  "password": "mi_password_seguro"
}
```

### GET `/api/auth/me`

Obtener perfil del usuario autenticado

```
Headers: Authorization: Bearer <token>
```

### GET `/api/auth/verify-token`

Verificar validez del token

```
Headers: Authorization: Bearer <token>
```

### POST `/api/auth/change-password`

Cambiar contraseña

```json
{
  "old_password": "password_actual",
  "new_password": "nuevo_password"
}
```

## 🗄️ Modelo de Base de Datos

### Tablas Principales

- **usuarios** - Información de usuarios
- **grupos** - Grupos colaborativos
- **usuarios_grupos** - Relación usuarios-grupos
- **categorias** - Categorías de gastos/ingresos
- **gastos** - Registro de gastos
- **ingresos** - Registro de ingresos
- **metas** - Metas financieras
- **aportes_metas** - Aportes a metas compartidas
- **historial_ai** - Historial de recomendaciones IA

## 🔧 Configuración

### Variables de Entorno

```env
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/gestion_gastos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gestion_gastos
DB_USER=usuario
DB_PASSWORD=password

# JWT
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
DEBUG=True
```

## 📚 Documentación API

Una vez ejecutada la aplicación, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén implementados)
pytest

# Ejecutar con cobertura
pytest --cov=.
```

## 🚀 Despliegue en Producción

1. **Configurar variables de entorno de producción**
2. **Usar base de datos PostgreSQL en la nube**
3. **Configurar HTTPS y certificados SSL**
4. **Implementar logging y monitoreo**
5. **Configurar backup automático de base de datos**

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

Desarrollado para estudiantes universitarios que buscan una gestión financiera inteligente y colaborativa.

---

**¡Disfruta gestionando tus finanzas de manera inteligente! 💰📊**
