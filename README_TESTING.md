# 🧪 Guía de Pruebas - Grupos e Invitaciones

Esta guía explica cómo probar el sistema completo de grupos e invitaciones.

## 📋 Requisitos Previos

1. Docker y Docker Compose instalados
2. Python 3.8+ instalado (para el script de pruebas)
3. Dependencias instaladas: `pip install -r requirements.txt`

## 🚀 Inicio Rápido

### Opción 1: Reiniciar Docker (Recomendado)

```bash
# Dar permisos de ejecución (solo la primera vez)
chmod +x restart_docker.sh

# Reiniciar Docker
./restart_docker.sh
```

Este script:
- Detiene los contenedores actuales
- Reconstruye las imágenes con los cambios más recientes
- Inicia los servicios
- Muestra el estado de los contenedores

### Opción 2: Comandos Manuales

```bash
# Detener contenedores
docker-compose down

# Reconstruir imágenes
docker-compose build --no-cache

# Iniciar contenedores
docker-compose up -d

# Ver logs
docker-compose logs -f api
```

## 🧪 Ejecutar Pruebas Automatizadas

El script `test_groups_invitations.py` automatiza todo el flujo de pruebas:

```bash
# Ejecutar el script de pruebas
python3 test_groups_invitations.py
```

### ¿Qué hace el script?

El script ejecuta el siguiente flujo completo:

1. ✅ **Espera a que la API esté disponible**
2. ✅ **Crea el Usuario 1** (`usuario1@test.com`)
3. ✅ **Crea el Usuario 2** (`usuario2@test.com`)
4. ✅ **Inicia sesión con Usuario 1**
5. ✅ **Crea un grupo** llamado "Grupo de Prueba"
6. ✅ **Genera una invitación** y obtiene el link
7. ✅ **Verifica la invitación** (sin autenticación)
8. ✅ **Inicia sesión con Usuario 2**
9. ✅ **Acepta la invitación** y se une al grupo
10. ✅ **Verifica que Usuario 2 está en el grupo**

### Salida del Script

El script muestra:
- ✅ Pasos exitosos en verde
- ❌ Errores en rojo
- ℹ️ Información importante en amarillo
- 🔵 Pasos principales en azul

Al final muestra un resumen con:
- IDs de usuarios creados
- ID del grupo
- Token de invitación
- Link de invitación

## 📝 Pruebas Manuales con Postman

### Flujo Completo Manual

1. **Registrar Usuario 1**
   - `POST /api/auth/register`
   - Body: `{"nombre": "Usuario Uno", "correo": "user1@test.com", "contrasena": "pass123", "moneda_preferida": "COP"}`

2. **Iniciar Sesión con Usuario 1**
   - `POST /api/auth/login`
   - Form data: `username=user1@test.com`, `password=pass123`
   - Guardar el `access_token` en la variable `{{access_token}}`

3. **Crear Grupo**
   - `POST /api/groups/`
   - Headers: `Authorization: Bearer {{access_token}}`
   - Body: `{"nombre": "Mi Grupo", "descripcion": "Descripción del grupo"}`
   - Guardar el `id_grupo` en `{{group_id}}`

4. **Crear Invitación**
   - `POST /api/invitations/`
   - Headers: `Authorization: Bearer {{access_token}}`
   - Body: `{"id_grupo": {{group_id}}, "dias_expiracion": 7}`
   - Guardar el `token` en `{{invitation_token}}` y el `link_invitacion`

5. **Ver Invitación (Sin Autenticación)**
   - `GET /api/invitations/token/{{invitation_token}}`
   - No requiere autenticación
   - Muestra detalles del grupo

6. **Registrar Usuario 2**
   - `POST /api/auth/register`
   - Body: `{"nombre": "Usuario Dos", "correo": "user2@test.com", "contrasena": "pass123", "moneda_preferida": "COP"}`

7. **Iniciar Sesión con Usuario 2**
   - `POST /api/auth/login`
   - Form data: `username=user2@test.com`, `password=pass123`
   - Actualizar `{{access_token}}` con el nuevo token

8. **Aceptar Invitación**
   - `POST /api/invitations/accept`
   - Headers: `Authorization: Bearer {{access_token}}`
   - Body: `{"token": "{{invitation_token}}"}`

9. **Verificar Grupos del Usuario 2**
   - `GET /api/groups/`
   - Headers: `Authorization: Bearer {{access_token}}`
   - Debe mostrar el grupo al que se unió

10. **Ver Detalles del Grupo**
    - `GET /api/groups/{{group_id}}`
    - Headers: `Authorization: Bearer {{access_token}}`
    - Muestra todos los miembros del grupo

## 🔍 Verificación de Resultados

### Verificar en la Base de Datos

```bash
# Conectarse a la base de datos
docker exec -it gestion_gastos_db psql -U usuario -d gestion_gastos

# Ver usuarios creados
SELECT id_usuario, nombre, correo FROM usuarios;

# Ver grupos creados
SELECT id_grupo, nombre, creado_por FROM grupos;

# Ver miembros de grupos
SELECT ug.id_usuario, u.nombre, ug.id_grupo, g.nombre, ug.rol 
FROM usuarios_grupos ug
JOIN usuarios u ON ug.id_usuario = u.id_usuario
JOIN grupos g ON ug.id_grupo = g.id_grupo;

# Ver invitaciones
SELECT id_invitacion, id_grupo, token, estado, fecha_creacion 
FROM invitaciones;
```

## 🐛 Solución de Problemas

### La API no responde

```bash
# Verificar que los contenedores estén corriendo
docker-compose ps

# Ver logs del API
docker-compose logs api

# Reiniciar el contenedor del API
docker-compose restart api
```

### Error de conexión a la base de datos

```bash
# Verificar que la base de datos esté corriendo
docker-compose ps db

# Ver logs de la base de datos
docker-compose logs db

# Verificar conexión
docker exec -it gestion_gastos_db psql -U usuario -d gestion_gastos -c "SELECT 1;"
```

### Error al crear invitación

- Verificar que el usuario sea administrador del grupo
- Verificar que el grupo exista
- Revisar los logs: `docker-compose logs api`

### El script de pruebas falla

- Verificar que la API esté corriendo: `curl http://localhost:8000/health`
- Verificar que `requests` esté instalado: `pip install requests`
- Revisar los logs de la API para más detalles

## 📊 Endpoints Disponibles

### Grupos
- `POST /api/groups/` - Crear grupo
- `GET /api/groups/` - Listar grupos del usuario
- `GET /api/groups/created` - Grupos creados por el usuario
- `GET /api/groups/{id}` - Detalles del grupo
- `PUT /api/groups/{id}` - Actualizar grupo
- `DELETE /api/groups/{id}` - Eliminar grupo
- `GET /api/groups/{id}/members` - Listar miembros
- `DELETE /api/groups/{id}/members/{user_id}` - Remover miembro
- `PUT /api/groups/{id}/members/{user_id}/role` - Cambiar rol

### Invitaciones
- `POST /api/invitations/` - Crear invitación
- `GET /api/invitations/group/{group_id}` - Invitaciones del grupo
- `GET /api/invitations/token/{token}` - Ver invitación (público)
- `GET /api/invitations/{id}/qr` - Generar QR
- `POST /api/invitations/accept` - Aceptar invitación
- `POST /api/invitations/reject` - Rechazar invitación
- `DELETE /api/invitations/{id}` - Revocar invitación

## 🎯 Próximos Pasos

1. Probar el flujo completo con el script automatizado
2. Probar manualmente con Postman
3. Probar la generación de QR codes
4. Probar la expiración de invitaciones
5. Probar permisos (admin vs miembro)

## 📚 Documentación Adicional

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

