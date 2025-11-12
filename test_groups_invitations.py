#!/usr/bin/env python3
"""
Script de pruebas automatizado para el sistema de grupos e invitaciones
Este script prueba el flujo completo:
1. Crear dos usuarios
2. Iniciar sesión con el primer usuario
3. Crear un grupo
4. Generar una invitación y obtener la URL
5. Iniciar sesión con el segundo usuario
6. Ver la invitación usando el token
7. Aceptar la invitación y unirse al grupo
"""

import requests
import json
import time
from typing import Dict, Optional

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Colores para la salida
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_step(step: int, message: str):
    """Imprimir un paso del proceso"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== Paso {step}: {message} ==={Colors.RESET}")

def print_success(message: str):
    """Imprimir mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    """Imprimir mensaje de error"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    """Imprimir información"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def wait_for_api(max_retries: int = 30, delay: int = 2):
    """Esperar a que la API esté disponible"""
    print_info("Esperando a que la API esté disponible...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print_success("API disponible")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(delay)
        print(f"Intento {i+1}/{max_retries}...")
    print_error("La API no está disponible")
    return False

def register_user(email: str, password: str, nombre: str) -> Optional[Dict]:
    """Registrar un nuevo usuario"""
    url = f"{API_BASE}/auth/register"
    data = {
        "nombre": nombre,
        "correo": email,
        "contrasena": password,
        "moneda_preferida": "COP"
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            return response.json()
        else:
            print_error(f"Error al registrar usuario: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print_error(f"Excepción al registrar usuario: {str(e)}")
        return None

def login_user(email: str, password: str) -> Optional[str]:
    """Iniciar sesión y obtener token"""
    url = f"{API_BASE}/auth/login"
    data = {
        "username": email,
        "password": password
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print_error(f"Error al iniciar sesión: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print_error(f"Excepción al iniciar sesión: {str(e)}")
        return None

def create_group(token: str, nombre: str, descripcion: str) -> Optional[Dict]:
    """Crear un grupo"""
    url = f"{API_BASE}/groups/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "nombre": nombre,
        "descripcion": descripcion
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            return response.json()
        else:
            print_error(f"Error al crear grupo: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print_error(f"Excepción al crear grupo: {str(e)}")
        return None

def create_invitation(token: str, group_id: int, dias_expiracion: int = 7) -> Optional[Dict]:
    """Crear una invitación para un grupo"""
    url = f"{API_BASE}/invitations/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "id_grupo": group_id,
        "id_usuario_invitado": None,
        "dias_expiracion": dias_expiracion
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            return response.json()
        else:
            print_error(f"Error al crear invitación: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print_error(f"Excepción al crear invitación: {str(e)}")
        return None

def get_invitation_by_token(token: str) -> Optional[Dict]:
    """Obtener detalles de una invitación por token (sin autenticación)"""
    url = f"{API_BASE}/invitations/token/{token}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Error al obtener invitación: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print_error(f"Excepción al obtener invitación: {str(e)}")
        return None

def accept_invitation(user_token: str, invitation_token: str) -> bool:
    """Aceptar una invitación"""
    url = f"{API_BASE}/invitations/accept"
    headers = {"Authorization": f"Bearer {user_token}"}
    data = {
        "token": invitation_token
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return True
        else:
            print_error(f"Error al aceptar invitación: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción al aceptar invitación: {str(e)}")
        return False

def get_user_groups(token: str) -> Optional[list]:
    """Obtener grupos del usuario"""
    url = f"{API_BASE}/groups/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Error al obtener grupos: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Excepción al obtener grupos: {str(e)}")
        return None

def get_group_details(token: str, group_id: int) -> Optional[Dict]:
    """Obtener detalles de un grupo"""
    url = f"{API_BASE}/groups/{group_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Error al obtener detalles del grupo: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Excepción al obtener detalles del grupo: {str(e)}")
        return None

def main():
    """Función principal del script de pruebas"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("SCRIPT DE PRUEBAS - GRUPOS E INVITACIONES")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # Esperar a que la API esté disponible
    if not wait_for_api():
        return
    
    # Datos de prueba (con timestamp para evitar conflictos)
    import time
    timestamp = int(time.time())
    usuario1_email = f"usuario1_{timestamp}@test.com"
    usuario1_password = "password123"
    usuario1_nombre = "Usuario Uno"
    
    usuario2_email = f"usuario2_{timestamp}@test.com"
    usuario2_password = "password123"
    usuario2_nombre = "Usuario Dos"
    
    grupo_nombre = "Grupo de Prueba"
    grupo_descripcion = "Grupo creado para probar el sistema de invitaciones"
    
    # Paso 1: Crear primer usuario
    print_step(1, f"Crear primer usuario: {usuario1_email}")
    user1 = register_user(usuario1_email, usuario1_password, usuario1_nombre)
    if not user1:
        print_error("No se pudo crear el primer usuario")
        return
    print_success(f"Usuario creado: {user1.get('nombre')} (ID: {user1.get('id_usuario')})")
    
    # Paso 2: Crear segundo usuario
    print_step(2, f"Crear segundo usuario: {usuario2_email}")
    user2 = register_user(usuario2_email, usuario2_password, usuario2_nombre)
    if not user2:
        print_error("No se pudo crear el segundo usuario")
        return
    print_success(f"Usuario creado: {user2.get('nombre')} (ID: {user2.get('id_usuario')})")
    
    # Paso 3: Iniciar sesión con el primer usuario
    print_step(3, f"Iniciar sesión con {usuario1_email}")
    token1 = login_user(usuario1_email, usuario1_password)
    if not token1:
        print_error("No se pudo iniciar sesión con el primer usuario")
        return
    print_success("Sesión iniciada correctamente")
    print_info(f"Token obtenido: {token1[:20]}...")
    
    # Paso 4: Crear grupo
    print_step(4, f"Crear grupo: {grupo_nombre}")
    group = create_group(token1, grupo_nombre, grupo_descripcion)
    if not group:
        print_error("No se pudo crear el grupo")
        return
    group_id = group.get('id_grupo')
    print_success(f"Grupo creado: {group.get('nombre')} (ID: {group_id})")
    
    # Paso 5: Crear invitación
    print_step(5, "Crear invitación para el grupo")
    invitation = create_invitation(token1, group_id, dias_expiracion=7)
    if not invitation:
        print_error("No se pudo crear la invitación")
        return
    invitation_token = invitation.get('token')
    invitation_link = invitation.get('link_invitacion')
    print_success("Invitación creada exitosamente")
    print_info(f"Token de invitación: {invitation_token}")
    print_info(f"Link de invitación: {invitation_link}")
    
    # Paso 6: Ver invitación (sin autenticación)
    print_step(6, "Ver detalles de la invitación (sin autenticación)")
    invitation_details = get_invitation_by_token(invitation_token)
    if not invitation_details:
        print_error("No se pudo obtener los detalles de la invitación")
        return
    print_success("Detalles de la invitación obtenidos")
    print_info(f"Grupo: {invitation_details.get('grupo_nombre')}")
    print_info(f"Descripción: {invitation_details.get('grupo_descripcion')}")
    print_info(f"Creador: {invitation_details.get('creador_nombre')}")
    print_info(f"Estado: {invitation_details.get('estado')}")
    
    # Paso 7: Iniciar sesión con el segundo usuario
    print_step(7, f"Iniciar sesión con {usuario2_email}")
    token2 = login_user(usuario2_email, usuario2_password)
    if not token2:
        print_error("No se pudo iniciar sesión con el segundo usuario")
        return
    print_success("Sesión iniciada correctamente")
    
    # Verificar que el usuario 2 NO está en el grupo aún
    print_info("Verificando que el usuario 2 NO está en el grupo...")
    groups_before = get_user_groups(token2)
    if groups_before is not None:
        group_ids_before = [g.get('id_grupo') for g in groups_before]
        if group_id not in group_ids_before:
            print_success("Confirmado: Usuario 2 NO está en el grupo")
        else:
            print_error("Usuario 2 ya está en el grupo (no debería estar)")
    
    # Paso 8: Aceptar invitación
    print_step(8, "Aceptar invitación y unirse al grupo")
    if accept_invitation(token2, invitation_token):
        print_success("Invitación aceptada exitosamente")
    else:
        print_error("No se pudo aceptar la invitación")
        return
    
    # Paso 9: Verificar que el usuario 2 ahora está en el grupo
    print_step(9, "Verificar que el usuario 2 está en el grupo")
    groups_after = get_user_groups(token2)
    if groups_after is not None:
        group_ids_after = [g.get('id_grupo') for g in groups_after]
        if group_id in group_ids_after:
            print_success(f"Usuario 2 ahora está en el grupo {group_id}")
        else:
            print_error("Usuario 2 NO está en el grupo después de aceptar")
    
    # Obtener detalles del grupo para ver los miembros
    group_details = get_group_details(token2, group_id)
    if group_details:
        print_info(f"Total de miembros: {group_details.get('total_miembros')}")
        miembros = group_details.get('miembros', [])
        print_info("Miembros del grupo:")
        for miembro in miembros:
            rol_icon = "👑" if miembro.get('rol') == 'admin' else "👤"
            print(f"  {rol_icon} {miembro.get('nombre')} ({miembro.get('correo')}) - Rol: {miembro.get('rol')}")
    
    # Resumen final
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}")
    print("PRUEBAS COMPLETADAS EXITOSAMENTE")
    print(f"{'='*60}{Colors.RESET}\n")
    print(f"{Colors.BOLD}Resumen:{Colors.RESET}")
    print(f"  • Usuario 1: {usuario1_email} (ID: {user1.get('id_usuario')})")
    print(f"  • Usuario 2: {usuario2_email} (ID: {user2.get('id_usuario')})")
    print(f"  • Grupo: {grupo_nombre} (ID: {group_id})")
    print(f"  • Token de invitación: {invitation_token}")
    print(f"  • Link de invitación: {invitation_link}")
    print(f"\n{Colors.YELLOW}Nota: Puedes usar el link de invitación para probar desde el frontend{Colors.RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.RESET}")
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

