# 🏗️ Arquitectura MVC - Sistema de Gestión de Gastos

## 📊 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                       │
│                    (Vista - Separada)                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP Requests/Responses
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                CONTROLADORES                            │   │
│  │              (app/controllers/)                        │   │
│  │                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐              │   │
│  │  │ AuthController  │  │ UserController   │              │   │
│  │  │                 │  │                 │              │   │
│  │  │ • /api/auth/*  │  │ • /api/users/*  │              │   │
│  │  │ • register     │  │ • profile       │              │   │
│  │  │ • login        │  │ • update        │              │   │
│  │  │ • verify       │  │                 │              │   │
│  │  └─────────────────┘  └─────────────────┘              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                │                               │
│                                │ Usa                           │
│                                ▼                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  SERVICIOS                              │   │
│  │               (app/services/)                          │   │
│  │                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐              │   │
│  │  │ AuthService      │  │ UserService      │              │   │
│  │  │                 │  │                 │              │   │
│  │  │ • create_token  │  │ • create_user   │              │   │
│  │  │ • authenticate  │  │ • get_user      │              │   │
│  │  │ • verify_token  │  │ • update_user    │              │   │
│  │  └─────────────────┘  └─────────────────┘              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                │                               │
│                                │ Usa                           │
│                                ▼                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  MODELOS                               │   │
│  │                (app/models/)                           │   │
│  │                                                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │   │
│  │  │ Usuario │ │ Grupo   │ │ Gasto   │ │ Ingreso  │      │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │   │
│  │                                                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │   │
│  │  │Categoria│ │ Meta    │ │AporteMeta│ │HistorialAI│     │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                │                               │
│                                │ Mapea a                       │
│                                ▼                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                BASE DE DATOS                           │   │
│  │                (PostgreSQL)                            │   │
│  │                                                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │   │
│  │  │usuarios │ │grupos   │ │gastos   │ │ingresos │      │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │   │
│  │                                                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │   │
│  │  │categorias│ │metas   │ │aportes_metas│ │historial_ai│   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Flujo de Datos MVC

### **1. REQUEST (HTTP)**

```
Cliente → Controlador
```

### **2. CONTROLADOR → SERVICIO**

```
Controlador recibe request → Llama a Servicio
```

### **3. SERVICIO → MODELO**

```
Servicio ejecuta lógica de negocio → Usa Modelo
```

### **4. MODELO → BASE DE DATOS**

```
Modelo mapea datos → Persiste en PostgreSQL
```

### **5. RESPUESTA (HTTP)**

```
Base de datos → Modelo → Servicio → Controlador → Cliente
```

## 📁 Estructura de Archivos

```
backend-gestion-gastos/
├── app/                          # 🏠 Paquete principal
│   ├── main.py                  # 🚀 Aplicación FastAPI
│   │
│   ├── core/                    # ⚙️ Configuración central
│   │   ├── config.py           # 🔧 Configuración
│   │   ├── database.py         # 🗄️ Base de datos
│   │   └── security.py         # 🔐 Seguridad
│   │
│   ├── models/                  # 📊 MODELOS (Datos)
│   │   ├── user.py            # 👤 Usuario
│   │   ├── group.py            # 👥 Grupo
│   │   ├── category.py         # 📂 Categoría
│   │   ├── expense.py          # 💸 Gasto
│   │   ├── income.py           # 💰 Ingreso
│   │   ├── goal.py             # 🎯 Meta
│   │   ├── user_group.py       # 👥 UsuarioGrupo
│   │   ├── goal_contribution.py # 💳 AporteMeta
│   │   └── ai_history.py       # 🤖 HistorialAI
│   │
│   ├── schemas/                 # 📋 ESQUEMAS (Validación)
│   │   ├── user.py            # 👤 Esquemas Usuario
│   │   ├── auth.py             # 🔐 Esquemas Auth
│   │   ├── category.py         # 📂 Esquemas Categoría
│   │   ├── expense.py          # 💸 Esquemas Gasto
│   │   └── income.py           # 💰 Esquemas Ingreso
│   │
│   ├── services/                # 🔧 SERVICIOS (Lógica)
│   │   ├── user_service.py    # 👤 Servicio Usuario
│   │   └── auth_service.py     # 🔐 Servicio Auth
│   │
│   └── controllers/              # 🎮 CONTROLADORES (HTTP)
│       ├── auth_controller.py  # 🔐 Controlador Auth
│       └── user_controller.py  # 👤 Controlador Usuario
│
├── main.py                      # 🚀 Punto de entrada
├── requirements.txt             # 📦 Dependencias
├── Dockerfile                   # 🐳 Imagen Docker
├── docker-compose.yml           # 🐳 Orquestación
└── bd.sql                      # 🗄️ Script BD
```

## 🎯 Responsabilidades por Capa

### **🎮 CONTROLADORES**

- **Responsabilidad**: Manejo de requests HTTP
- **Tecnología**: FastAPI routers
- **Contenido**: Endpoints de la API
- **Ejemplo**: `POST /api/auth/login`

### **🔧 SERVICIOS**

- **Responsabilidad**: Lógica de negocio
- **Tecnología**: Clases Python
- **Contenido**: Operaciones CRUD y reglas de negocio
- **Ejemplo**: `UserService.create_user()`

### **📊 MODELOS**

- **Responsabilidad**: Representación de datos
- **Tecnología**: SQLAlchemy ORM
- **Contenido**: Mapeo de tablas de BD
- **Ejemplo**: `class Usuario(Base)`

### **📋 ESQUEMAS**

- **Responsabilidad**: Validación de datos
- **Tecnología**: Pydantic models
- **Contenido**: Estructuras de request/response
- **Ejemplo**: `class UsuarioCreate(BaseModel)`

## ✅ Ventajas de la Arquitectura MVC

### **🔍 Separación Clara**

- Cada capa tiene una responsabilidad específica
- Fácil localizar funcionalidades
- Código organizado y modular

### **📈 Escalabilidad**

- Fácil agregar nuevos controladores
- Servicios reutilizables
- Modelos independientes

### **🛠️ Mantenibilidad**

- Código fácil de mantener
- Testing independiente por capas
- Cambios aislados por capa

### **♻️ Reutilización**

- Servicios compartidos entre controladores
- Modelos consistentes
- Esquemas reutilizables

## 🚀 Cómo Ejecutar

### **Con Docker**

```bash
docker-compose up -d
```

### **Localmente**

```bash
pip install -r requirements.txt
python main.py
```

## 📚 Endpoints Disponibles

### **Autenticación**

- `POST /api/auth/register` - Registro
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Perfil
- `GET /api/auth/verify-token` - Verificar token
- `POST /api/auth/change-password` - Cambiar contraseña

### **Usuarios**

- `GET /api/users/profile` - Obtener perfil
- `PUT /api/users/profile` - Actualizar perfil

---

**¡Arquitectura MVC implementada exitosamente! 🎉**

La separación de responsabilidades permite un desarrollo más organizado, mantenible y escalable.
