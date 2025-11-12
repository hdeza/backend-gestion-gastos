#!/usr/bin/env python3
"""
Script de pruebas automatizado para ingresos y gastos (personales y grupales)
Este script prueba el flujo completo:
1. Crear dos usuarios
2. Crear un grupo
3. Crear ingresos personales y de grupo
4. Crear gastos personales y de grupo
5. Verificar totales y filtros
"""

import requests
import json
import time
from typing import Dict, Optional
from decimal import Decimal

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

def create_invitation(token: str, group_id: int) -> Optional[Dict]:
    """Crear una invitación"""
    url = f"{API_BASE}/invitations/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "id_grupo": group_id,
        "dias_expiracion": 7
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            return response.json()
        else:
            print_error(f"Error al crear invitación: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Excepción al crear invitación: {str(e)}")
        return None

def accept_invitation(user_token: str, invitation_token: str) -> bool:
    """Aceptar una invitación"""
    url = f"{API_BASE}/invitations/accept"
    headers = {"Authorization": f"Bearer {user_token}"}
    data = {"token": invitation_token}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 200
    except:
        return False

def create_income(token: str, descripcion: str, monto: float, fecha: str, grupo_id: Optional[int] = None) -> Optional[Dict]:
    """Crear un ingreso"""
    url = f"{API_BASE}/incomes/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "descripcion": descripcion,
        "monto": monto,
        "fecha": fecha,
        "fuente": "Prueba",
        "id_categoria": None,
        "id_grupo": grupo_id
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            return response.json()
        else:
            print_error(f"Error al crear ingreso: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Excepción al crear ingreso: {str(e)}")
        return None

def create_expense(token: str, descripcion: str, monto: float, fecha: str, grupo_id: Optional[int] = None) -> Optional[Dict]:
    """Crear un gasto"""
    url = f"{API_BASE}/expenses/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "descripcion": descripcion,
        "monto": monto,
        "fecha": fecha,
        "metodo_pago": "efectivo",
        "nota": "Gasto de prueba",
        "recurrente": False,
        "id_categoria": None,
        "id_grupo": grupo_id
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            return response.json()
        else:
            print_error(f"Error al crear gasto: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Excepción al crear gasto: {str(e)}")
        return None

def get_incomes(token: str, personal_only: bool = False) -> Optional[list]:
    """Obtener ingresos"""
    url = f"{API_BASE}/incomes/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"personal_only": str(personal_only).lower()}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_expenses(token: str, personal_only: bool = False) -> Optional[list]:
    """Obtener gastos"""
    url = f"{API_BASE}/expenses/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"personal_only": str(personal_only).lower()}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_group_incomes(token: str, group_id: int) -> Optional[list]:
    """Obtener ingresos de grupo"""
    url = f"{API_BASE}/incomes/group/{group_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_group_expenses(token: str, group_id: int) -> Optional[list]:
    """Obtener gastos de grupo"""
    url = f"{API_BASE}/expenses/group/{group_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_total_income(token: str, personal_only: bool = False) -> Optional[float]:
    """Obtener total de ingresos"""
    url = f"{API_BASE}/incomes/total/amount"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"personal_only": str(personal_only).lower()}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("total_ingresos", 0.0)
        return None
    except:
        return None

def get_total_expense(token: str, personal_only: bool = False) -> Optional[float]:
    """Obtener total de gastos"""
    url = f"{API_BASE}/expenses/total/amount"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"personal_only": str(personal_only).lower()}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("total_gastos", 0.0)
        return None
    except:
        return None

def get_group_total_income(token: str, group_id: int) -> Optional[float]:
    """Obtener total de ingresos de grupo"""
    url = f"{API_BASE}/incomes/group/{group_id}/total/amount"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("total_ingresos", 0.0)
        return None
    except:
        return None

def get_group_total_expense(token: str, group_id: int) -> Optional[float]:
    """Obtener total de gastos de grupo"""
    url = f"{API_BASE}/expenses/group/{group_id}/total/amount"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("total_gastos", 0.0)
        return None
    except:
        return None

def main():
    """Función principal del script de pruebas"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("SCRIPT DE PRUEBAS - INGRESOS Y GASTOS")
    print(f"{'='*60}{Colors.RESET}\n")
    
    if not wait_for_api():
        return
    
    # Datos de prueba
    import time
    timestamp = int(time.time())
    usuario1_email = f"user1_{timestamp}@test.com"
    usuario1_password = "password123"
    usuario1_nombre = "Usuario Uno"
    
    usuario2_email = f"user2_{timestamp}@test.com"
    usuario2_password = "password123"
    usuario2_nombre = "Usuario Dos"
    
    grupo_nombre = "Grupo de Prueba Financiera"
    
    # Paso 1: Crear usuarios
    print_step(1, "Crear usuarios de prueba")
    user1 = register_user(usuario1_email, usuario1_password, usuario1_nombre)
    if not user1:
        return
    print_success(f"Usuario 1 creado: {user1.get('nombre')}")
    
    user2 = register_user(usuario2_email, usuario2_password, usuario2_nombre)
    if not user2:
        return
    print_success(f"Usuario 2 creado: {user2.get('nombre')}")
    
    # Paso 2: Iniciar sesión con usuario 1
    print_step(2, "Iniciar sesión con Usuario 1")
    token1 = login_user(usuario1_email, usuario1_password)
    if not token1:
        return
    print_success("Sesión iniciada")
    
    # Paso 3: Crear grupo
    print_step(3, "Crear grupo")
    group = create_group(token1, grupo_nombre, "Grupo para pruebas financieras")
    if not group:
        return
    group_id = group.get('id_grupo')
    print_success(f"Grupo creado: {group.get('nombre')} (ID: {group_id})")
    
    # Paso 4: Invitar usuario 2 al grupo
    print_step(4, "Invitar Usuario 2 al grupo")
    invitation = create_invitation(token1, group_id)
    if not invitation:
        return
    invitation_token = invitation.get('token')
    print_success("Invitación creada")
    
    # Paso 5: Usuario 2 acepta invitación
    print_step(5, "Usuario 2 acepta invitación")
    token2 = login_user(usuario2_email, usuario2_password)
    if not token2:
        return
    
    if accept_invitation(token2, invitation_token):
        print_success("Usuario 2 se unió al grupo")
    else:
        print_error("No se pudo unir al grupo")
        return
    
    # Paso 6: Crear ingresos personales del Usuario 1
    print_step(6, "Crear ingresos personales del Usuario 1")
    income1_personal = create_income(token1, "Salario personal", 2000000.00, "2024-01-15")
    income2_personal = create_income(token1, "Freelance personal", 500000.00, "2024-01-20")
    
    if income1_personal and income2_personal:
        print_success(f"Ingreso 1 personal creado: {income1_personal.get('descripcion')} - ${income1_personal.get('monto')}")
        print_success(f"Ingreso 2 personal creado: {income2_personal.get('descripcion')} - ${income2_personal.get('monto')}")
    else:
        print_error("Error al crear ingresos personales")
    
    # Paso 7: Crear ingresos de grupo
    print_step(7, "Crear ingresos de grupo")
    income1_group = create_income(token1, "Ingreso grupal 1", 1000000.00, "2024-01-10", group_id)
    income2_group = create_income(token2, "Ingreso grupal 2", 800000.00, "2024-01-12", group_id)
    
    if income1_group and income2_group:
        print_success(f"Ingreso grupal 1 creado: {income1_group.get('descripcion')} - ${income1_group.get('monto')}")
        print_success(f"Ingreso grupal 2 creado: {income2_group.get('descripcion')} - ${income2_group.get('monto')}")
    else:
        print_error("Error al crear ingresos grupales")
    
    # Paso 8: Crear gastos personales del Usuario 1
    print_step(8, "Crear gastos personales del Usuario 1")
    expense1_personal = create_expense(token1, "Almuerzo personal", 25000.00, "2024-01-16")
    expense2_personal = create_expense(token1, "Transporte personal", 15000.00, "2024-01-17")
    
    if expense1_personal and expense2_personal:
        print_success(f"Gasto 1 personal creado: {expense1_personal.get('descripcion')} - ${expense1_personal.get('monto')}")
        print_success(f"Gasto 2 personal creado: {expense2_personal.get('descripcion')} - ${expense2_personal.get('monto')}")
    else:
        print_error("Error al crear gastos personales")
    
    # Paso 9: Crear gastos de grupo
    print_step(9, "Crear gastos de grupo")
    expense1_group = create_expense(token1, "Gasto grupal 1", 50000.00, "2024-01-11", group_id)
    expense2_group = create_expense(token2, "Gasto grupal 2", 30000.00, "2024-01-13", group_id)
    
    if expense1_group and expense2_group:
        print_success(f"Gasto grupal 1 creado: {expense1_group.get('descripcion')} - ${expense1_group.get('monto')}")
        print_success(f"Gasto grupal 2 creado: {expense2_group.get('descripcion')} - ${expense2_group.get('monto')}")
    else:
        print_error("Error al crear gastos grupales")
    
    # Paso 10: Verificar ingresos personales del Usuario 1
    print_step(10, "Verificar ingresos personales del Usuario 1")
    personal_incomes = get_incomes(token1, personal_only=True)
    if personal_incomes:
        print_success(f"Total ingresos personales: {len(personal_incomes)}")
        print_info(f"Ingresos: {[i.get('descripcion') for i in personal_incomes]}")
    else:
        print_error("No se pudieron obtener ingresos personales")
    
    # Paso 11: Verificar todos los ingresos del Usuario 1
    print_step(11, "Verificar todos los ingresos del Usuario 1 (personales + grupo)")
    all_incomes = get_incomes(token1, personal_only=False)
    if all_incomes:
        print_success(f"Total ingresos (todos): {len(all_incomes)}")
    
    # Paso 12: Verificar ingresos de grupo
    print_step(12, "Verificar ingresos de grupo")
    group_incomes = get_group_incomes(token1, group_id)
    if group_incomes:
        print_success(f"Total ingresos del grupo: {len(group_incomes)}")
        print_info(f"Ingresos del grupo: {[i.get('descripcion') for i in group_incomes]}")
    
    # Paso 13: Verificar gastos personales del Usuario 1
    print_step(13, "Verificar gastos personales del Usuario 1")
    personal_expenses = get_expenses(token1, personal_only=True)
    if personal_expenses:
        print_success(f"Total gastos personales: {len(personal_expenses)}")
        print_info(f"Gastos: {[e.get('descripcion') for e in personal_expenses]}")
    
    # Paso 14: Verificar todos los gastos del Usuario 1
    print_step(14, "Verificar todos los gastos del Usuario 1 (personales + grupo)")
    all_expenses = get_expenses(token1, personal_only=False)
    if all_expenses:
        print_success(f"Total gastos (todos): {len(all_expenses)}")
    
    # Paso 15: Verificar gastos de grupo
    print_step(15, "Verificar gastos de grupo")
    group_expenses = get_group_expenses(token1, group_id)
    if group_expenses:
        print_success(f"Total gastos del grupo: {len(group_expenses)}")
        print_info(f"Gastos del grupo: {[e.get('descripcion') for e in group_expenses]}")
    
    # Paso 16: Verificar totales personales
    print_step(16, "Verificar totales personales del Usuario 1")
    total_income_personal = get_total_income(token1, personal_only=True)
    total_expense_personal = get_total_expense(token1, personal_only=True)
    
    if total_income_personal is not None:
        print_success(f"Total ingresos personales: ${total_income_personal:,.2f}")
    if total_expense_personal is not None:
        print_success(f"Total gastos personales: ${total_expense_personal:,.2f}")
        balance_personal = total_income_personal - total_expense_personal
        print_info(f"Balance personal: ${balance_personal:,.2f}")
    
    # Paso 17: Verificar totales de grupo
    print_step(17, "Verificar totales del grupo")
    total_income_group = get_group_total_income(token1, group_id)
    total_expense_group = get_group_total_expense(token1, group_id)
    
    if total_income_group is not None:
        print_success(f"Total ingresos del grupo: ${total_income_group:,.2f}")
    if total_expense_group is not None:
        print_success(f"Total gastos del grupo: ${total_expense_group:,.2f}")
        balance_group = total_income_group - total_expense_group
        print_info(f"Balance del grupo: ${balance_group:,.2f}")
    
    # Resumen final
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}")
    print("PRUEBAS COMPLETADAS EXITOSAMENTE")
    print(f"{'='*60}{Colors.RESET}\n")
    print(f"{Colors.BOLD}Resumen:{Colors.RESET}")
    print(f"  • Usuario 1: {usuario1_email}")
    print(f"  • Usuario 2: {usuario2_email}")
    print(f"  • Grupo: {grupo_nombre} (ID: {group_id})")
    print(f"\n{Colors.BOLD}Ingresos:{Colors.RESET}")
    print(f"  • Personales Usuario 1: {len(personal_incomes) if personal_incomes else 0}")
    print(f"  • Totales Usuario 1: {len(all_incomes) if all_incomes else 0}")
    print(f"  • Del grupo: {len(group_incomes) if group_incomes else 0}")
    print(f"\n{Colors.BOLD}Gastos:{Colors.RESET}")
    print(f"  • Personales Usuario 1: {len(personal_expenses) if personal_expenses else 0}")
    print(f"  • Totales Usuario 1: {len(all_expenses) if all_expenses else 0}")
    print(f"  • Del grupo: {len(group_expenses) if group_expenses else 0}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.RESET}")
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

