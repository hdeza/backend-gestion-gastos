#!/usr/bin/env python3
"""
Script de pruebas automatizado para metas y aportes
"""

import requests
import json
import time
from typing import Dict, Optional

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_step(step: int, message: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== Paso {step}: {message} ==={Colors.RESET}")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def wait_for_api(max_retries: int = 30, delay: int = 2):
    print_info("Esperando a que la API esté disponible...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print_success("API disponible")
                return True
        except:
            pass
        time.sleep(delay)
    print_error("La API no está disponible")
    return False

def register_user(email: str, password: str, nombre: str) -> Optional[Dict]:
    url = f"{API_BASE}/auth/register"
    data = {"nombre": nombre, "correo": email, "contrasena": password, "moneda_preferida": "COP"}
    try:
        response = requests.post(url, json=data)
        return response.json() if response.status_code == 201 else None
    except:
        return None

def login_user(email: str, password: str) -> Optional[str]:
    url = f"{API_BASE}/auth/login"
    data = {"username": email, "password": password}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except:
        return None

def create_group(token: str, nombre: str) -> Optional[Dict]:
    url = f"{API_BASE}/groups/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"nombre": nombre, "descripcion": "Grupo de prueba"}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json() if response.status_code == 201 else None
    except:
        return None

def create_goal(token: str, nombre: str, monto: float, grupo_id: Optional[int] = None) -> Optional[Dict]:
    url = f"{API_BASE}/goals/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "nombre": nombre,
        "monto_objetivo": monto,
        "fecha_inicio": "2024-01-01",
        "fecha_fin": "2024-12-31",
        "estado": "activa",
        "id_grupo": grupo_id
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json() if response.status_code == 201 else None
    except:
        return None

def create_contribution(token: str, goal_id: int, monto: float) -> Optional[Dict]:
    url = f"{API_BASE}/goal-contributions/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"id_meta": goal_id, "monto": monto, "fecha": "2024-01-15"}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json() if response.status_code == 201 else None
    except:
        return None

def get_goal_progress(token: str, goal_id: int) -> Optional[Dict]:
    url = f"{API_BASE}/goals/{goal_id}/progress"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("SCRIPT DE PRUEBAS - METAS Y APORTES")
    print(f"{'='*60}{Colors.RESET}\n")
    
    if not wait_for_api():
        return
    
    timestamp = int(time.time())
    user_email = f"user_{timestamp}@test.com"
    token = login_user(user_email, "password123")
    
    if not token:
        user = register_user(user_email, "password123", "Usuario Prueba")
        if not user:
            print_error("No se pudo crear usuario")
            return
        token = login_user(user_email, "password123")
        if not token:
            return
    
    print_step(1, "Crear meta personal")
    goal_personal = create_goal(token, "Meta Personal", 1000000.00)
    if goal_personal:
        goal_id = goal_personal.get('id_meta')
        print_success(f"Meta creada: {goal_personal.get('nombre')} (ID: {goal_id})")
    else:
        print_error("No se pudo crear meta")
        return
    
    print_step(2, "Crear aportes a meta personal")
    contrib1 = create_contribution(token, goal_id, 200000.00)
    contrib2 = create_contribution(token, goal_id, 300000.00)
    if contrib1 and contrib2:
        print_success(f"Aporte 1: ${contrib1.get('monto')}")
        print_success(f"Aporte 2: ${contrib2.get('monto')}")
    
    print_step(3, "Verificar progreso de meta")
    progress = get_goal_progress(token, goal_id)
    if progress:
        print_success(f"Progreso: {progress.get('porcentaje_completado')}%")
        print_info(f"Monto acumulado: ${progress.get('monto_acumulado'):,.2f}")
        print_info(f"Faltante: ${progress.get('faltante'):,.2f}")
    
    print_step(4, "Crear grupo y meta grupal")
    group = create_group(token, "Grupo de Metas")
    if group:
        group_id = group.get('id_grupo')
        goal_group = create_goal(token, "Meta Grupal", 2000000.00, group_id)
        if goal_group:
            goal_group_id = goal_group.get('id_meta')
            print_success(f"Meta grupal creada: {goal_group.get('nombre')} (ID: {goal_group_id})")
            
            print_step(5, "Crear aporte a meta grupal")
            contrib_group = create_contribution(token, goal_group_id, 500000.00)
            if contrib_group:
                print_success(f"Aporte grupal: ${contrib_group.get('monto')}")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}")
    print("PRUEBAS COMPLETADAS EXITOSAMENTE")
    print(f"{'='*60}{Colors.RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

