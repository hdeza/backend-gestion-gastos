# 🚀 Guía de Uso - Colección Postman

## 📋 Descripción

Esta colección de Postman contiene todos los endpoints necesarios para probar la **API de Gestión de Gastos** con arquitectura MVC.

## 🛠️ Configuración Inicial

### **1. Importar Colección y Entorno**

1. **Abrir Postman**
2. **Importar Colección**:

   - Click en "Import"
   - Seleccionar `Postman_Collection.json`
   - Click "Import"

3. **Importar Entorno**:

   - Click en "Import"
   - Seleccionar `Postman_Environment.json`
   - Click "Import"

4. **Seleccionar Entorno**:
   - En la esquina superior derecha, seleccionar "Gestión de Gastos - Desarrollo"

### **2. Verificar Configuración**

- **Base URL**: `http://localhost:8000`
- **Entorno**: "Gestión de Gastos - Desarrollo"
- **Variables**: Configuradas automáticamente

## 🚀 Flujo de Pruebas Recomendado

### **Paso 1: Verificar API**

1. **Root Endpoint** - Verificar que la API esté funcionando
2. **Health Check** - Confirmar estado saludable

### **Paso 2: Autenticación**

1. **Registro de Usuario** - Crear un nuevo usuario
2. **Iniciar Sesión** - Obtener token JWT (se guarda automáticamente)
3. **Verificar Token** - Confirmar que el token funciona
4. **Obtener Perfil** - Ver información del usuario

### **Paso 3: Gestión de Usuario**

1. **Obtener Perfil de Usuario** - Ver perfil completo
2. **Actualizar Perfil** - Modificar información

### **Paso 4: Tests de Errores**

1. **Login con Credenciales Incorrectas** - Verificar manejo de errores
2. **Registro con Email Duplicado** - Confirmar validaciones
3. **Acceso sin Token** - Verificar seguridad
4. **Acceso con Token Inválido** - Confirmar validación JWT

## 🔧 Características de la Colección

### **✅ Tests Automáticos**

- **Status Code**: Verifica que las respuestas sean exitosas
- **Response Time**: Confirma que las respuestas sean rápidas (< 2 segundos)
- **Token Auto-save**: Guarda automáticamente el token JWT del login

### **✅ Variables de Entorno**

- **`base_url`**: URL base de la API
- **`access_token`**: Token JWT (se llena automáticamente)
- **`user_email`**: Email del usuario de prueba
- **`user_password`**: Contraseña del usuario de prueba

### **✅ Organización por Carpetas**

- **🏠 Health Check**: Verificación de estado
- **🔐 Autenticación**: Login, registro, tokens
- **👤 Gestión de Usuarios**: Perfil y actualizaciones
- **🧪 Tests de Errores**: Validación de manejo de errores
- **📊 Documentación API**: Acceso a Swagger y ReDoc

## 📚 Endpoints Incluidos

### **🔐 Autenticación**

- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Inicio de sesión
- `GET /api/auth/me` - Perfil del usuario autenticado
- `GET /api/auth/verify-token` - Verificar token
- `POST /api/auth/change-password` - Cambiar contraseña

### **👤 Gestión de Usuarios**

- `GET /api/users/profile` - Obtener perfil
- `PUT /api/users/profile` - Actualizar perfil

### **🏠 Verificación**

- `GET /` - Endpoint raíz
- `GET /health` - Health check

## 🎯 Ejemplos de Uso

### **Registro de Usuario**

```json
{
  "nombre": "Juan Pérez",
  "correo": "juan@ejemplo.com",
  "contrasena": "mi_password_seguro",
  "moneda_preferida": "COP"
}
```

### **Login**

```
username: juan@ejemplo.com
password: mi_password_seguro
```

### **Actualizar Perfil**

```json
{
  "nombre": "Juan Carlos Pérez",
  "moneda_preferida": "USD",
  "foto_perfil": "https://ejemplo.com/foto.jpg"
}
```

## 🔍 Verificación de Respuestas

### **Respuesta Exitosa (200)**

```json
{
  "id_usuario": 1,
  "nombre": "Juan Pérez",
  "correo": "juan@ejemplo.com",
  "moneda_preferida": "COP",
  "fecha_registro": "2024-01-15T10:30:00",
  "tipo_usuario": "normal"
}
```

### **Token JWT**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### **Error de Validación (400)**

```json
{
  "detail": "El correo electrónico ya está registrado"
}
```

### **Error de Autenticación (401)**

```json
{
  "detail": "No se pudieron validar las credenciales"
}
```

## 🚨 Solución de Problemas

### **Error de Conexión**

- Verificar que la API esté ejecutándose en `http://localhost:8000`
- Comprobar que Docker esté funcionando: `docker-compose ps`

### **Error 401 Unauthorized**

- Verificar que el token JWT sea válido
- Hacer login nuevamente para obtener un nuevo token

### **Error 422 Validation Error**

- Verificar que los datos enviados cumplan con el esquema
- Revisar tipos de datos y campos requeridos

### **Error 500 Internal Server Error**

- Verificar logs de la aplicación
- Comprobar conexión a la base de datos

## 📖 Documentación Adicional

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🎉 ¡Listo para Probar!

Con esta colección puedes probar completamente tu API de gestión de gastos con arquitectura MVC. Los tests automáticos te ayudarán a verificar que todo funcione correctamente.

**¡Disfruta probando tu API! 🚀**
