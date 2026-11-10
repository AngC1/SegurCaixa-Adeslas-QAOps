"""
Orquestador Maestro QAOps — Ayesa Digital para SegurCaixa Adeslas (/servicios-para-clientes).
Levanta el portal simulado (si no está ya activo), ejecuta:
  1. Diagnóstico del Servidor MCP de Selenium (Self-Healing DOM + Flujos MCP).
  2. Suite completa Pytest + Selenium E2E (SCA-TC-001 a SCA-TC-010).
  3. Motor de Rendimiento JMeter Asistido por IA (SCA-TC-011 y SCA-TC-012).
  4. Verificación del Hub ALM (Jira Xray, TestLink, Redmine).
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
BASE_URL = "http://127.0.0.1:8080"


def is_portal_up() -> bool:
    try:
        r = requests.get(f"{BASE_URL}/api/v1/health", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False


def main() -> int:
    server_proc = None
    try:
        if not is_portal_up():
            print("[1/4] Iniciando Simulador Portal SegurCaixa Adeslas y Hub ALM en http://127.0.0.1:8080 ...")
            server_proc = subprocess.Popen(
                [sys.executable, str(ROOT / "portal-adeslas" / "app.py")],
                cwd=str(ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for _ in range(25):
                if is_portal_up():
                    break
                time.sleep(0.3)
            if not is_portal_up():
                print("ERROR: No se pudo iniciar el servidor en el puerto 8080.")
                return 1
        else:
            print("[1/4] Portal SegurCaixa Adeslas detectado activo en http://127.0.0.1:8080")

        print("\n[2/4] Ejecutando Self-Test del Servidor MCP de Selenium (Inspección DOM + Flujos IA)...")
        rc_mcp = subprocess.call(
            [sys.executable, str(ROOT / "mcp-selenium-server" / "server.py"), "--selftest"],
            cwd=str(ROOT),
        )
        if rc_mcp != 0:
            return rc_mcp

        print("\n[3/4] Ejecutando Suite Automatizada Pytest + Selenium POM (SCA-TC-001 .. SCA-TC-010)...")
        rc_pytest = subprocess.call(
            [sys.executable, "-m", "pytest", "selenium-qaops/tests/test_servicios_clientes_e2e.py", "-v"],
            cwd=str(ROOT),
        )
        if rc_pytest != 0:
            return rc_pytest

        print("\n[4/4] Ejecutando Prueba de Carga y Diagnóstico con JMeter Asistido por IA (SCA-TC-011 .. SCA-TC-012)...")
        rc_jmeter = subprocess.call(
            [sys.executable, str(ROOT / "jmeter-ai" / "ai_jmeter_assistant.py"), "--vus", "12", "--iterations", "5"],
            cwd=str(ROOT),
        )
        if rc_jmeter != 0:
            return rc_jmeter

        alm = requests.get(f"{BASE_URL}/api/v1/alm/backlog", timeout=5).json()["backlog"]
        passed = sum(1 for tc in alm["testCases"] if tc["status"] == "PASSED")
        total = len(alm["testCases"])
        print("\n================================================================================")
        print(f"CERTIFICACIÓN QAOPS COMPLETADA: {passed}/{total} Test Cases PASSED en Hub ALM")
        print(f" - Portal Servicios para Clientes : {BASE_URL}/servicios-para-clientes")
        print(f" - Hub ALM (Jira/TestLink/Redmine): {BASE_URL}/alm-dashboard")
        print("================================================================================")
        return 0
    finally:
        if server_proc is not None:
            server_proc.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
