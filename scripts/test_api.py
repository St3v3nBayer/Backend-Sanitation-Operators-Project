"""
Script de pruebas automatizadas para el Sistema Tarifario
Prueba todos los endpoints principales y valida respuestas
"""

import requests
import json
from typing import Dict, Optional

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = None


class Colors:
    """Colores para terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_step(message: str):
    """Imprime un paso"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}📌 {message}{Colors.END}")


def print_success(message: str):
    """Imprime éxito"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message: str):
    """Imprime error"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message: str):
    """Imprime advertencia"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_json(data: dict, indent: int = 2):
    """Imprime JSON formateado"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def test_health():
    """Prueba el endpoint de salud"""
    print_step("Test 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        
        print_success(f"Status: {data['status']}")
        print_success(f"Version: {data['version']}")
        return True
    except Exception as e:
        print_error(f"Health check falló: {str(e)}")
        return False


def test_login() -> Optional[str]:
    """Prueba login y retorna token"""
    print_step("Test 2: Login")
    
    credentials = {
        "username": "admin@system.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
        assert response.status_code == 200
        
        data = response.json()
        token = data["access_token"]
        
        print_success("Login exitoso")
        print(f"  Token: {token[:50]}...")
        return token
    except Exception as e:
        print_error(f"Login falló: {str(e)}")
        return None


def test_get_companies(token: str):
    """Lista empresas"""
    print_step("Test 3: Listar Empresas")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/companies", headers=headers)
        assert response.status_code == 200
        
        companies = response.json()
        print_success(f"Encontradas {len(companies)} empresas:")
        
        for company in companies[:3]:  # Mostrar solo 3
            print(f"  • ID: {company['id']} - {company['name']}")
        
        return companies
    except Exception as e:
        print_error(f"Listar empresas falló: {str(e)}")
        return []


def test_get_aps(token: str, company_id: int):
    """Lista APS de una empresa"""
    print_step(f"Test 4: Listar APS de Empresa {company_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/aps/company/{company_id}",
            headers=headers
        )
        assert response.status_code == 200
        
        aps_list = response.json()
        print_success(f"Encontrados {len(aps_list)} APS:")
        
        for aps in aps_list:
            print(f"  • ID: {aps['id']} - {aps['name']} ({aps['code']})")
            print(f"    Municipio: {aps['municipality']}")
            print(f"    Segmento: {aps['segment']}")
            if aps.get('is_coastal_municipality'):
                print(f"    🌊 Municipio costero")
        
        return aps_list
    except Exception as e:
        print_error(f"Listar APS falló: {str(e)}")
        return []


def test_get_aps_summary(token: str, aps_id: int):
    """Obtiene resumen de un APS"""
    print_step(f"Test 5: Resumen de APS {aps_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/aps/{aps_id}/summary",
            headers=headers
        )
        assert response.status_code == 200
        
        summary = response.json()
        
        print_success("Resumen obtenido:")
        print(f"  • Distancia efectiva: {summary['effective_distance_km']} km")
        print(f"  • Meses registrados: {summary['total_months_registered']}")
        
        if summary.get('six_month_averages'):
            avg = summary['six_month_averages']
            print(f"  • Promedios 6 meses:")
            print(f"    - Suscriptores: {avg.get('num_subscribers_total', 0):,.0f}")
            print(f"    - Toneladas: {avg.get('tons_collected_non_recyclable', 0):,.1f}")
        
        return summary
    except Exception as e:
        print_error(f"Obtener resumen falló: {str(e)}")
        return None


def test_get_monthly_data(token: str, aps_id: int):
    """Lista datos mensuales"""
    print_step(f"Test 6: Datos Mensuales de APS {aps_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/aps/{aps_id}/monthly-data",
            headers=headers
        )
        assert response.status_code == 200
        
        data_list = response.json()
        print_success(f"Encontrados {len(data_list)} meses de datos:")
        
        for data in data_list[:3]:  # Mostrar solo 3
            print(f"  • {data['period']}: {data['num_subscribers_total']:,} suscriptores")
        
        return data_list
    except Exception as e:
        print_error(f"Listar datos mensuales falló: {str(e)}")
        return []


def test_calculate_tariff(token: str, aps_id: int, period: str = "2026-02"):
    """Calcula tarifa oficial"""
    print_step(f"Test 7: Calcular Tarifa - APS {aps_id} - {period}")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "aps_id": aps_id,
        "period": period,
        "calculation_type": "official"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/tariff/calculate",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 201:
            print_error(f"Status: {response.status_code}")
            print(response.text)
            return None
        
        calculation = response.json()
        
        print_success("Tarifa calculada exitosamente:")
        print(f"  • ID Cálculo: {calculation['id']}")
        print(f"\n  💰 COSTOS:")
        print(f"    - CFT (Costo Fijo Total): ${calculation['cft']:,.2f}")
        print(f"      • CCS (Comercialización): ${calculation['ccs']:,.2f}")
        print(f"      • CLUS (Limpieza Urbana): ${calculation['clus']:,.2f}")
        print(f"      • CBLS (Barrido): ${calculation['cbls']:,.2f}")
        print(f"\n    - CVNA (Costo Variable): ${calculation['cvna']:,.2f}/ton")
        print(f"      • CRT (Recolección): ${calculation['crt']:,.2f}")
        print(f"      • CDF (Disposición): ${calculation['cdf']:,.2f}")
        print(f"      • CTL (Lixiviados): ${calculation['ctl']:,.2f}")
        print(f"\n    - VBA (Aprovechamiento): ${calculation['vba']:,.2f}/ton")
        
        print(f"\n  📊 TARIFAS FINALES POR ESTRATO:")
        for i in range(1, 7):
            tariff = calculation.get(f'tariff_stratum_{i}_final', 0)
            print(f"    - Estrato {i}: ${tariff:,.2f}/mes")
        
        tariff_comm = calculation.get('tariff_commercial_final', 0)
        print(f"    - Comercial: ${tariff_comm:,.2f}/mes")
        
        # Alertas
        validations = calculation.get('validations', {})
        alerts = validations.get('alerts', [])
        if alerts:
            print(f"\n  ⚠️  ALERTAS:")
            for alert in alerts:
                print(f"    - {alert}")
        
        return calculation
    except Exception as e:
        print_error(f"Calcular tarifa falló: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_simulate_tariff(token: str, aps_id: int, period: str = "2026-02"):
    """Crea una simulación"""
    print_step(f"Test 8: Simular Escenario - APS {aps_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "aps_id": aps_id,
        "period": period,
        "is_simulation": True,
        "simulation_name": "Test: +20% suscriptores",
        "calculation_type": "simulation",
        "simulation_data": {
            "num_subscribers_total": 15000,
            "tons_collected_non_recyclable": 1020
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/tariff/simulate",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 201:
            print_error(f"Status: {response.status_code}")
            print(response.text)
            return None
        
        simulation = response.json()
        
        print_success("Simulación creada:")
        print(f"  • ID: {simulation['id']}")
        print(f"  • Nombre: {simulation.get('simulation_name', 'N/A')}")
        print(f"  • Tarifa E4: ${simulation.get('tariff_stratum_4_final', 0):,.2f}")
        
        return simulation
    except Exception as e:
        print_error(f"Simulación falló: {str(e)}")
        return None


def test_compare_calculations(token: str, calc_id_1: int, calc_id_2: int):
    """Compara dos cálculos"""
    print_step(f"Test 9: Comparar Cálculos {calc_id_1} vs {calc_id_2}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/tariff/compare",
            headers=headers,
            params={
                "calculation_id_1": calc_id_1,
                "calculation_id_2": calc_id_2
            }
        )
        
        if response.status_code != 200:
            print_error(f"Status: {response.status_code}")
            return None
        
        comparison = response.json()
        
        print_success("Comparación realizada:")
        
        if 'differences' in comparison:
            diffs = comparison['differences']
            
            for key, values in diffs.items():
                diff = values.get('diff', 0)
                diff_pct = values.get('diff_pct', 0)
                
                if diff != 0:
                    direction = "↑" if diff > 0 else "↓"
                    print(f"  • {key}: {direction} ${abs(diff):,.2f} ({diff_pct:+.2f}%)")
        
        if 'significant_changes' in comparison:
            changes = comparison['significant_changes']
            if changes:
                print(f"\n  🔴 Cambios significativos (>5%):")
                for change in changes:
                    print(f"    - {change['component']}: {change['change_pct']:+.2f}%")
        
        return comparison
    except Exception as e:
        print_error(f"Comparación falló: {str(e)}")
        return None


def test_calculation_history(token: str, aps_id: int):
    """Obtiene historial de cálculos"""
    print_step(f"Test 10: Historial de Cálculos - APS {aps_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/tariff/aps/{aps_id}/history",
            headers=headers,
            params={"only_official": False, "limit": 10}
        )
        
        if response.status_code != 200:
            print_error(f"Status: {response.status_code}")
            return []
        
        history = response.json()
        
        print_success(f"Encontrados {len(history)} cálculos:")
        
        for calc in history:
            calc_type = "🎭 Simulación" if calc.get('is_simulation') else "✅ Oficial"
            print(f"  • {calc_type} - ID: {calc['id']} - {calc['period']}")
            print(f"    Tarifa E4: ${calc.get('tariff_stratum_4_final', 0):,.2f}")
        
        return history
    except Exception as e:
        print_error(f"Historial falló: {str(e)}")
        return []


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print(f"{Colors.BOLD}🧪 SUITE DE PRUEBAS - SISTEMA TARIFARIO{Colors.END}")
    print("="*60)
    
    # Test 1: Health
    if not test_health():
        print_error("\n❌ El servidor no está respondiendo. Verifica que esté corriendo.")
        print(f"   Ejecuta: uvicorn app.main:app --reload")
        return
    
    # Test 2: Login
    token = test_login()
    if not token:
        print_error("\n❌ No se pudo obtener token. Verifica credenciales.")
        return
    
    # Test 3: Empresas
    companies = test_get_companies(token)
    if not companies:
        print_warning("No hay empresas. Ejecuta: python scripts/generate_test_data.py")
        return
    
    company_id = companies[0]['id']
    
    # Test 4: APS
    aps_list = test_get_aps(token, company_id)
    if not aps_list:
        print_warning("No hay APS para esta empresa.")
        return
    
    aps_id = aps_list[0]['id']
    
    # Test 5: Resumen APS
    test_get_aps_summary(token, aps_id)
    
    # Test 6: Datos mensuales
    monthly_data = test_get_monthly_data(token, aps_id)
    if not monthly_data:
        print_warning("No hay datos mensuales.")
        return
    
    # Test 7: Calcular tarifa
    calculation = test_calculate_tariff(token, aps_id)
    if not calculation:
        print_error("No se pudo calcular tarifa.")
        return
    
    calc_id = calculation['id']
    
    # Test 8: Simulación
    simulation = test_simulate_tariff(token, aps_id)
    
    # Test 9: Comparar (si hay simulación)
    if simulation:
        sim_id = simulation['id']
        test_compare_calculations(token, calc_id, sim_id)
    
    # Test 10: Historial
    test_calculation_history(token, aps_id)
    
    # Resumen final
    print("\n" + "="*60)
    print(f"{Colors.GREEN}{Colors.BOLD}✅ TODAS LAS PRUEBAS COMPLETADAS{Colors.END}")
    print("="*60)
    print(f"\n📊 Resumen:")
    print(f"  • Empresas: {len(companies)}")
    print(f"  • APS probado: {aps_id}")
    print(f"  • Cálculos realizados: 2 (1 oficial, 1 simulación)")
    print(f"\n🌐 Explora la API completa en: {BASE_URL}/docs")
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
