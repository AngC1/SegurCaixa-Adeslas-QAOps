"""
Simulador del Portal Web y API REST de SegurCaixa Adeslas (/servicios-para-clientes)
+ Hub ALM Unificado (Jira Xray / TestLink / Redmine) y Telemetría QAOps.
Desarrollado para la arquitectura de referencia QAOps de Ayesa Digital.
"""

from __future__ import annotations

import json
import os
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

from flask import Flask, Response, jsonify, redirect, render_template, request, send_file

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
ALM_JSON_PATH = PROJECT_ROOT / "alm-backlog" / "jira-xray" / "backlog_xray_export.json"
TESTLINK_XML_PATH = PROJECT_ROOT / "alm-backlog" / "testlink" / "segurcaixa_testplan_testlink.xml"
REDMINE_CSV_PATH = PROJECT_ROOT / "alm-backlog" / "redmine" / "redmine_issues_backlog.csv"

app = Flask(__name__, template_folder="templates", static_folder="static")

# ---------------------------------------------------------------------------
# Datos Maestros Simulados de SegurCaixa Adeslas (/servicios-para-clientes)
# ---------------------------------------------------------------------------

SERVICIOS_CATALOGO: List[Dict[str, Any]] = [
    {
        "id": "srv-cuadro-medico",
        "codigo": "CUADRO_MEDICO",
        "titulo": "Cuadro Médico y Centros",
        "descripcion": "Más de 43.000 profesionales sanitarios y 1.300 centros médicos y hospitalarios concertados en toda España.",
        "icono": "🏥",
        "sla_respuesta_ms": 150,
        "destacado": True,
        "tab_target": "tab-cuadro",
    },
    {
        "id": "srv-autorizaciones",
        "codigo": "AUTORIZACIONES",
        "titulo": "Autorizaciones Médicas Online",
        "descripcion": "Gestiona tus volantes y prescripciones para pruebas diagnósticas, ingresos o tratamientos sin desplazamientos.",
        "icono": "📋",
        "sla_respuesta_ms": 250,
        "destacado": True,
        "tab_target": "tab-autorizaciones",
    },
    {
        "id": "srv-reembolsos",
        "codigo": "REEMBOLSOS",
        "titulo": "Reembolso de Gastos Médicos",
        "descripcion": "Envía tus facturas médicas o farmacéuticas y recibe hasta el 90% de abono directo en tu cuenta bancaria.",
        "icono": "💶",
        "sla_respuesta_ms": 250,
        "destacado": True,
        "tab_target": "tab-reembolsos",
    },
    {
        "id": "srv-area-cliente",
        "codigo": "AREA_CLIENTE",
        "titulo": "Área Cliente y Tarjeta Digital",
        "descripcion": "Consulta tus pólizas, copagos, recibos y lleva siempre contigo tu Tarjeta Sanitaria Digital Adeslas.",
        "icono": "🪪",
        "sla_respuesta_ms": 180,
        "destacado": True,
        "tab_target": "tab-area-cliente",
    },
    {
        "id": "srv-videoconsulta",
        "codigo": "SALUD_DIGITAL",
        "titulo": "Videoconsulta y Orientación Médica 24h",
        "descripcion": "Habla con un médico especialista por videollamada, chat médico o teléfono de orientación sanitaria 24 horas.",
        "icono": "🩺",
        "sla_respuesta_ms": 200,
        "destacado": False,
        "tab_target": "tab-videoconsulta",
    },
    {
        "id": "srv-urgencias",
        "codigo": "URGENCIAS_24H",
        "titulo": "Urgencias Médicas y Dental 24h",
        "descripcion": "Acceso inmediato a hospitales de guardia, urgencias pediátricas, oftalmológicas y clínicas Adeslas Dental.",
        "icono": "🚑",
        "sla_respuesta_ms": 120,
        "destacado": False,
        "tab_target": "tab-cuadro",
    },
]

CUADRO_MEDICO_DB: List[Dict[str, Any]] = [
    {
        "id": "CM-MAD-001",
        "nombre": "Hospital Ruber Internacional - Grupo Quirónsalud",
        "facultativo": "Dr. Alejandro Vega Martín (Jefe de Unidad)",
        "provincia": "Madrid",
        "especialidad": "Cardiología",
        "direccion": "Calle de la Masó, 38, 28034 Madrid",
        "telefono": "913 875 000",
        "polizas": ["Adeslas Plena Plus", "Adeslas Plena Vital", "Adeslas Seniors", "Adeslas Premier", "Muface / Isfas"],
        "cita_online": True,
        "urgencias_24h": True,
        "copago": "0 € (Plena Plus / Premier)",
    },
    {
        "id": "CM-MAD-002",
        "nombre": "Centro Médico Adeslas Salud Madrid Príncipe de Vergara",
        "facultativo": "Dra. Elena Soriano Ruiz",
        "provincia": "Madrid",
        "especialidad": "Cardiología",
        "direccion": "Calle del Príncipe de Vergara, 204, 28002 Madrid",
        "telefono": "915 643 210",
        "polizas": ["Adeslas Plena Plus", "Adeslas Plena Vital", "Adeslas Seniors", "Muface / Isfas"],
        "cita_online": True,
        "urgencias_24h": False,
        "copago": "Según modalidad",
    },
    {
        "id": "CM-MAD-003",
        "nombre": "Hospital Universitario HM Sanchinarro",
        "facultativo": "Servicio de Urgencias Generales y Traumatológicas 24h",
        "provincia": "Madrid",
        "especialidad": "Urgencias 24h",
        "direccion": "Calle de Oña, 10, 28050 Madrid",
        "telefono": "917 567 800",
        "polizas": ["Adeslas Plena Plus", "Adeslas Plena Vital", "Adeslas Seniors", "Adeslas Premier", "Muface / Isfas"],
        "cita_online": True,
        "urgencias_24h": True,
        "copago": "Sin copago en urgencia vital",
    },
    {
        "id": "CM-MAD-004",
        "nombre": "Clínica Adeslas Dental Goya",
        "facultativo": "Dr. Javier Mendoza Ortiz",
        "provincia": "Madrid",
        "especialidad": "Dental",
        "direccion": "Calle de Goya, 115, 28009 Madrid",
        "telefono": "900 229 922",
        "polizas": ["Adeslas Plena Plus", "Adeslas Dental Max", "Adeslas Seniors", "Muface / Isfas"],
        "cita_online": True,
        "urgencias_24h": False,
        "copago": "Franquicia Dental Adeslas",
    },
    {
        "id": "CM-BCN-001",
        "nombre": "Centro Médico Teknon - Barcelona",
        "facultativo": "Dra. Montserrat Puigvert Bosch",
        "provincia": "Barcelona",
        "especialidad": "Dermatología",
        "direccion": "Carrer de Vilana, 12, 08022 Barcelona",
        "telefono": "932 906 200",
        "polizas": ["Adeslas Plena Plus", "Adeslas Plena Vital", "Adeslas Premier"],
        "cita_online": True,
        "urgencias_24h": True,
        "copago": "0 € (Plena Plus)",
    },
    {
        "id": "CM-BCN-002",
        "nombre": "Hospital Quirónsalud Barcelona",
        "facultativo": "Unidad de Urgencias 24h y Pediatría",
        "provincia": "Barcelona",
        "especialidad": "Urgencias 24h",
        "direccion": "Plaça d'Alfonso Comín, 5, 08023 Barcelona",
        "telefono": "932 554 000",
        "polizas": ["Adeslas Plena Plus", "Adeslas Plena Vital", "Adeslas Seniors", "Muface / Isfas"],
        "cita_online": True,
        "urgencias_24h": True,
        "copago": "0 €",
    },
    {
        "id": "CM-SEV-001",
        "nombre": "Hospital Quirónsalud Sagrado Corazón Sevilla",
        "facultativo": "Dr. Manuel Domínguez Romero",
        "provincia": "Sevilla",
        "especialidad": "Traumatología",
        "direccion": "Calle Rafael Salgado, 3, 41013 Sevilla",
        "telefono": "954 937 676",
        "polizas": ["Adeslas Plena Plus", "Adeslas Plena Vital", "Adeslas Seniors", "Muface / Isfas"],
        "cita_online": True,
        "urgencias_24h": True,
        "copago": "0 €",
    },
    {
        "id": "CM-VAL-001",
        "nombre": "Hospital Vithas Valencia 9 de Octubre",
        "facultativo": "Dra. Carmen Albornoz Gil",
        "provincia": "Valencia",
        "especialidad": "Pediatría",
        "direccion": "Carrer de la Vall de la Ballestera, 59, 46015 València",
        "telefono": "963 179 100",
        "polizas": ["Adeslas Plena Plus", "Adeslas Plena Vital", "Muface / Isfas"],
        "cita_online": True,
        "urgencias_24h": True,
        "copago": "0 €",
    },
    {
        "id": "CM-BIL-001",
        "nombre": "Clínica IMQ Zorrotzaurre (Concierto Adeslas País Vasco)",
        "facultativo": "Dr. Iñaki Etxebarria Goikoetxea",
        "provincia": "Bilbao",
        "especialidad": "Cardiología",
        "direccion": "Ballets Olaeta Kalea, 4, 48014 Bilbo",
        "telefono": "944 755 000",
        "polizas": ["Adeslas Plena Plus", "Adeslas Premier", "Muface / Isfas"],
        "cita_online": True,
        "urgencias_24h": True,
        "copago": "0 €",
    },
]

CLIENTES_DB: Dict[str, Dict[str, Any]] = {
    "12345678Z": {
        "nif": "12345678Z",
        "password": "Adeslas2026!",
        "nombre": "Carlos Martínez Gómez",
        "num_poliza": "POL-SCA-908122",
        "num_tarjeta": "8000123456789012",
        "modalidad": "Adeslas Plena Plus + Reembolso Premier",
        "fecha_alta": "15/01/2021",
        "estado_poliza": "ACTIVA - AL CORRIENTE DE PAGO",
        "copago_acumulado_anual": "0,00 € (Modalidad Sin Copago)",
        "beneficiarios": [
            {"nombre": "Carlos Martínez Gómez (Titular)", "tarjeta": "8000123456789012"},
            {"nombre": "Lucía Martínez Fernández (Asegurada)", "tarjeta": "8000123456789013"},
        ],
    },
    "87654321X": {
        "nif": "87654321X",
        "password": "Adeslas2026!",
        "nombre": "Marta Sánchez Alcázar",
        "num_poliza": "POL-SCA-774510",
        "num_tarjeta": "8000987654321098",
        "modalidad": "Adeslas Mutualistas Muface",
        "fecha_alta": "01/02/2019",
        "estado_poliza": "ACTIVA - CONCIERTO MUFACE",
        "copago_acumulado_anual": "0,00 €",
        "beneficiarios": [
            {"nombre": "Marta Sánchez Alcázar (Titular)", "tarjeta": "8000987654321098"},
        ],
    },
}

AUTORIZACIONES_REGISTRADAS: List[Dict[str, Any]] = []
REEMBOLSOS_REGISTRADOS: List[Dict[str, Any]] = []
CITAS_REGISTRADAS: List[Dict[str, Any]] = []

JMETER_LATEST_REPORT: Dict[str, Any] = {
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    "scenario": "Campaña Salud Invierno - Servicios para Clientes (12 VUs / 60 muestras)",
    "totalSamples": 60,
    "throughputRps": 44.8,
    "avgResponseMs": 32.4,
    "p90Ms": 64.0,
    "p95Ms": 72.27,
    "p99Ms": 94.5,
    "errorRatePct": 0.0,
    "apdex": 1.0,
    "slaStatus": "PASSED",
    "aiInsights": [
        "Cumplimiento SLA Global: APROBADO (P95 = 72.27 ms frente al objetivo < 450.0 ms; Error Rate = 0.0%).",
        "Índice de satisfacción de usuario Apdex = 1.0 con un caudal sostenido de 44.8 req/s (60 transacciones).",
        "Detección de Anomalía IA en 'POST /api/v1/autorizaciones (Estudio Genético)': P95 superior a la media general por validación síncrona de baremos de inspección médica. Acción recomendada vinculada a SCA-BUG-201: activar caché Redis.",
    ],
    "endpoints": [
        {"label": "GET /api/v1/cuadro-medico", "samples": 24, "avgMs": 14.2, "p95Ms": 26.0, "errorPct": 0.0},
        {"label": "POST /api/v1/autorizaciones", "samples": 12, "avgMs": 18.4, "p95Ms": 31.0, "errorPct": 0.0},
        {"label": "POST /api/v1/autorizaciones (Estudio Genético)", "samples": 12, "avgMs": 68.5, "p95Ms": 76.2, "errorPct": 0.0},
        {"label": "POST /api/v1/reembolsos", "samples": 12, "avgMs": 16.9, "p95Ms": 28.5, "errorPct": 0.0},
    ],
}

SELENIUM_LATEST_REPORT: Dict[str, Any] = {
    "runId": "XRAY-EXEC-2026-103",
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    "browser": "Google Chrome Headless 1440x950 (Selenium WebDriver 4.52)",
    "mcpServer": "ayesa-selenium-qaops v1.0.0 (JSON-RPC 2.0 stdio)",
    "domLocatorsExtracted": 40,
    "domPruningSavingPct": 92.4,
    "selfHealingEventsCount": 0,
    "selfHealingStatus": "ACTIVE · 40/40 Selectores Primarios Verificados (0 Roturas)",
    "totalDurationMs": 5480,
    "passed": 10,
    "failed": 0,
    "total": 10,
    "screenshotUrl": "/api/v1/qaops/screenshot/mcp_selftest_servicios_clientes.png",
    "mcpToolRuns": [
        {
            "tool": "selenium_start_session",
            "target": "http://127.0.0.1:8080/servicios-para-clientes",
            "durationMs": 610,
            "status": "PASSED",
            "output": "Sesión Chrome Headless activa (1440x950)",
        },
        {
            "tool": "selenium_inspect_dom_locators",
            "target": "DOM Pruning (button, input, select, [data-testid])",
            "durationMs": 145,
            "status": "PASSED",
            "output": "40 selectores extraídos (-92.4% ahorro de tokens de contexto)",
        },
        {
            "tool": "selenium_execute_adeslas_flow (cuadro_medico)",
            "target": "Provincia=Madrid, Especialidad=Cardiología",
            "durationMs": 397,
            "status": "PASSED",
            "output": "2 centros concertados verificados en Madrid",
        },
        {
            "tool": "selenium_execute_adeslas_flow (autorizacion)",
            "target": "Tarjeta=8000123456789012, Prescripción=RX-99281",
            "durationMs": 395,
            "status": "PASSED",
            "output": "Estado AUTORIZADA · Código AUT-2026 generado",
        },
        {
            "tool": "selenium_take_screenshot",
            "target": "selenium-qaops/reports/mcp_selftest_servicios_clientes.png",
            "durationMs": 180,
            "status": "PASSED",
            "output": "Evidencia PNG almacenada (85 KB)",
        },
        {
            "tool": "alm_sync_test_result",
            "target": "POST /api/v1/qaops/test-runs",
            "durationMs": 42,
            "status": "PASSED",
            "output": "Sincronizado con Jira Xray / TestLink / Redmine",
        },
    ],
    "testCasesDetail": [
        {
            "key": "SCA-TC-001",
            "testLinkId": "TL-SCA-101",
            "name": "test_tc001_catalogo_servicios_clientes",
            "locatorPrimary": "#hero-title / #catalogo-servicios-grid .service-card",
            "locatorFallback": "[data-testid='hero-title'] / [data-testid^='service-card-']",
            "assertion": "6 tarjetas de servicio renderizadas y KPIs visibles",
            "durationMs": 620,
            "status": "PASSED",
        },
        {
            "key": "SCA-TC-002",
            "testLinkId": "TL-SCA-102",
            "name": "test_tc002_busqueda_cuadro_medico_madrid_cardiologia",
            "locatorPrimary": "#cm-provincia + #cm-especialidad + #btn-buscar-cuadro",
            "locatorFallback": "[data-testid='select-provincia'] + [data-testid='btn-buscar-cuadro']",
            "assertion": ">= 2 centros en Madrid con Cardiología (Ruber / Príncipe de Vergara)",
            "durationMs": 540,
            "status": "PASSED",
        },
        {
            "key": "SCA-TC-003",
            "testLinkId": "TL-SCA-103",
            "name": "test_tc003_busqueda_urgencias_muface",
            "locatorPrimary": "#cm-especialidad + #cm-poliza + #btn-buscar-cuadro",
            "locatorFallback": "[data-testid='select-poliza'] -> Muface / Isfas",
            "assertion": ">= 2 hospitales con Urgencias 24h concertados para Muface",
            "durationMs": 510,
            "status": "PASSED",
        },
        {
            "key": "SCA-TC-004",
            "testLinkId": "TL-SCA-104",
            "name": "test_tc004_solicitud_autorizacion_exitosa",
            "locatorPrimary": "#aut-tarjeta + #aut-tipo-acto + #btn-solicitar-autorizacion",
            "locatorFallback": "[data-testid='input-aut-tarjeta'] + [data-testid='aut-resultado-alert']",
            "assertion": "Estado == AUTORIZADA y código AUT-2026-XXXXX generado",
            "durationMs": 590,
            "status": "PASSED",
        },
        {
            "key": "SCA-TC-005",
            "testLinkId": "TL-SCA-105",
            "name": "test_tc005_autorizacion_tarjeta_invalida",
            "locatorPrimary": "#aut-tarjeta (valor '12345') + #aut-resultado-alert",
            "locatorFallback": "[data-testid='aut-resultado-alert']",
            "assertion": "Rechazo HTTP 400 + Alerta 'entre 12 y 16 dígitos numéricos'",
            "durationMs": 480,
            "status": "PASSED",
        },
        {
            "key": "SCA-TC-006",
            "testLinkId": "TL-SCA-106",
            "name": "test_tc006_autorizacion_revision_medica",
            "locatorPrimary": "POST /api/v1/autorizaciones (Estudio Genético Oncológico)",
            "locatorFallback": "Contrato SDD RN-AUT-02",
            "assertion": "Estado == PENDIENTE_REVISION_MEDICA (SLA 48h)",
            "durationMs": 110,
            "status": "PASSED",
        },
        {
            "key": "SCA-TC-007",
            "testLinkId": "TL-SCA-107",
            "name": "test_tc007_reembolso_premier_calculo_90",
            "locatorPrimary": "#rmb-nif + #rmb-modalidad + #rmb-importe + #rmb-iban",
            "locatorFallback": "[data-testid='rmb-importe-abonado']",
            "assertion": "Expediente RMB-2026-XXXXX y abono exacto 225.00 EUR (90% de 250 EUR)",
            "durationMs": 640,
            "status": "PASSED",
        },
        {
            "key": "SCA-TC-008",
            "testLinkId": "TL-SCA-108",
            "name": "test_tc008_reembolso_iban_invalido",
            "locatorPrimary": "#rmb-iban (valor 'ES1234') + #rmb-resultado-alert",
            "locatorFallback": "[data-testid='rmb-resultado-alert']",
            "assertion": "Rechazo HTTP 400 + Alerta formato IBAN ES + 22 dígitos",
            "durationMs": 470,
            "status": "PASSED",
        },
        {
            "key": "SCA-TC-009",
            "testLinkId": "TL-SCA-109",
            "name": "test_tc009_login_area_cliente_tarjeta_digital",
            "locatorPrimary": "#login-nif + #login-password + #btn-login-cliente",
            "locatorFallback": "[data-testid='tarjeta-digital-adeslas']",
            "assertion": "Titular Carlos Martínez Gómez + Póliza POL-SCA-908122 + Tarjeta Digital",
            "durationMs": 580,
            "status": "PASSED",
        },
        {
            "key": "SCA-TC-010",
            "testLinkId": "TL-SCA-110",
            "name": "test_tc010_reserva_videoconsulta_medica",
            "locatorPrimary": "#vc-especialidad + #vc-motivo + #btn-reservar-vc",
            "locatorFallback": "[data-testid='vc-codigo-cita']",
            "assertion": "Cita confirmada CIT-2026-XXXXX + Dra. Patricia Navarro Solís",
            "durationMs": 540,
            "status": "PASSED",
        },
    ],
}

EXECUTION_HISTORY: List[Dict[str, Any]] = [
    {
        "execKey": "SCA-EXEC-2026-003",
        "buildName": "Build #103 · Suite Pytest + Selenium POM (E2E)",
        "runner": "Pytest + Selenium WebDriver (Chrome Headless)",
        "environment": "Local Simulation (127.0.0.1:8080)",
        "testsScope": "SCA-TC-001 .. SCA-TC-010 (10 tests)",
        "passed": 10,
        "failed": 0,
        "durationMs": 5480,
        "status": "PASSED",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    },
    {
        "execKey": "SCA-EXEC-2026-002",
        "buildName": "Build #102 · Diagnóstico Servidor MCP de Selenium (--selftest)",
        "runner": "Agente IA via MCP Server (ayesa-selenium-qaops)",
        "environment": "Local Simulation (127.0.0.1:8080)",
        "testsScope": "DOM Pruning (40 locators) + Flujos Cuadro Médico & Autorizaciones",
        "passed": 6,
        "failed": 0,
        "durationMs": 1769,
        "status": "PASSED",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    },
    {
        "execKey": "SCA-EXEC-2026-001",
        "buildName": "Build #101 · Performance Gate JMeter Asistido por IA",
        "runner": "JMeter AI Assistant (ai_jmeter_assistant.py)",
        "environment": "Local Simulation (12 VUs / 60 muestras)",
        "testsScope": "SCA-TC-011 .. SCA-TC-012 (P95 = 72.27ms, Apdex = 1.0)",
        "passed": 2,
        "failed": 0,
        "durationMs": 1420,
        "status": "PASSED",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    },
]


def load_alm_backlog() -> Dict[str, Any]:
    if ALM_JSON_PATH.exists():
        with open(ALM_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"project": {}, "epics": [], "userStories": [], "testPlan": {}, "testCases": [], "defects": []}


def save_alm_backlog(data: Dict[str, Any]) -> None:
    ALM_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ALM_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Rutas Vistas HTML (Portal SegurCaixa Adeslas + Dashboard ALM QAOps)
# ---------------------------------------------------------------------------


@app.route("/")
def root_redirect():
    return redirect("/servicios-para-clientes")


@app.route("/servicios-para-clientes")
def servicios_para_clientes_view():
    return render_template(
        "servicios_clientes.html",
        servicios=SERVICIOS_CATALOGO,
        cuadro_inicial=CUADRO_MEDICO_DB,
    )


@app.route("/alm-dashboard")
def alm_dashboard_view():
    alm_data = load_alm_backlog()
    return render_template(
        "alm_dashboard.html",
        alm=alm_data,
        jmeter=JMETER_LATEST_REPORT,
        selenium=SELENIUM_LATEST_REPORT,
        executions=EXECUTION_HISTORY,
    )


@app.route("/presentacion")
def presentacion_ejecutiva_view():
    pres_html = PROJECT_ROOT / "presentacion" / "index.html"
    if pres_html.exists():
        return send_file(pres_html)
    return redirect("/servicios-para-clientes")


# ---------------------------------------------------------------------------
# Endpoints API REST (/api/v1/*) para Frontend, Selenium y JMeter AI
# ---------------------------------------------------------------------------


@app.route("/api/v1/health", methods=["GET"])
def api_health():
    return jsonify(
        {
            "status": "UP",
            "service": "segurcaixa-adeslas-servicios-clientes-sim",
            "qaopsProvider": "Ayesa Digital",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "centrosCuadroMedico": len(CUADRO_MEDICO_DB),
                "autorizacionesTramitadas": len(AUTORIZACIONES_REGISTRADAS),
                "reembolsosTramitados": len(REEMBOLSOS_REGISTRADOS),
                "citasAgendadas": len(CITAS_REGISTRADAS),
            },
        }
    )


@app.route("/api/v1/servicios", methods=["GET"])
def api_servicios():
    return jsonify({"total": len(SERVICIOS_CATALOGO), "servicios": SERVICIOS_CATALOGO})


@app.route("/api/v1/cuadro-medico", methods=["GET"])
def api_cuadro_medico():
    provincia = request.args.get("provincia", "").strip()
    especialidad = request.args.get("especialidad", "").strip()
    poliza = request.args.get("poliza", "").strip()
    q = request.args.get("q", "").strip().lower()
    urgencias = request.args.get("urgencias24h", "").strip().lower()

    resultados = []
    for item in CUADRO_MEDICO_DB:
        if provincia and provincia != "Todas" and item["provincia"].lower() != provincia.lower():
            continue
        if especialidad and especialidad != "Todas" and item["especialidad"].lower() != especialidad.lower():
            continue
        if poliza and poliza != "Todas":
            if not any(poliza.lower() in p.lower() for p in item["polizas"]):
                continue
        if urgencias in ("true", "1", "si") and not item["urgencias_24h"]:
            continue
        if q:
            texto = f"{item['nombre']} {item['facultativo']} {item['direccion']} {item['especialidad']}".lower()
            if q not in texto:
                continue
        resultados.append(item)

    return jsonify(
        {
            "filtros": {
                "provincia": provincia or "Todas",
                "especialidad": especialidad or "Todas",
                "poliza": poliza or "Todas",
                "q": q,
            },
            "total": len(resultados),
            "resultados": resultados,
        }
    )


@app.route("/api/v1/autorizaciones", methods=["POST"])
def api_crear_autorizacion():
    payload = request.get_json(silent=True) or {}
    num_tarjeta = str(payload.get("numTarjeta", "")).strip().replace(" ", "")
    tipo_acto = str(payload.get("tipoActo", "")).strip()
    cod_prescripcion = str(payload.get("codigoPrescripcion", "")).strip()
    centro_medico = str(payload.get("centroMedico", "")).strip()
    observaciones = str(payload.get("observaciones", "")).strip()

    if not re.fullmatch(r"\d{12,16}", num_tarjeta):
        return (
            jsonify(
                {
                    "ok": False,
                    "errorCode": "INVALID_CARD_NUMBER",
                    "mensaje": "El número de Tarjeta Adeslas debe contener entre 12 y 16 dígitos numéricos (ej. 8000123456789012).",
                }
            ),
            400,
        )

    if not tipo_acto or not cod_prescripcion or not centro_medico:
        return (
            jsonify(
                {
                    "ok": False,
                    "errorCode": "MISSING_REQUIRED_FIELDS",
                    "mensaje": "Todos los campos obligatorios (Tipo de prueba, Código de prescripción y Centro médico) deben completarse.",
                }
            ),
            400,
        )

    # Simulación de latencia mayor en estudios genéticos para que JMeter AI detecte el patrón
    es_compleja = "genético" in tipo_acto.lower() or "genetico" in tipo_acto.lower() or "oncol" in tipo_acto.lower()
    if es_compleja:
        time.sleep(0.06)
        estado = "PENDIENTE_REVISION_MEDICA"
        mensaje = "Su solicitud requiere valoración por la Inspección Médica de SegurCaixa Adeslas (plazo máximo 48h laborables)."
    else:
        estado = "AUTORIZADA"
        mensaje = "Autorización médica concedida automáticamente. Puede acudir a su centro médico con este código."

    codigo_aut = f"AUT-2026-{random.randint(10000, 99999)}"
    registro = {
        "codigoAutorizacion": codigo_aut,
        "numTarjeta": num_tarjeta,
        "tipoActo": tipo_acto,
        "codigoPrescripcion": cod_prescripcion,
        "centroMedico": centro_medico,
        "observaciones": observaciones,
        "estado": estado,
        "mensaje": mensaje,
        "fechaSolicitud": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    AUTORIZACIONES_REGISTRADAS.append(registro)
    return jsonify({"ok": True, "autorizacion": registro}), 201


@app.route("/api/v1/reembolsos", methods=["POST"])
def api_crear_reembolso():
    payload = request.get_json(silent=True) or {}
    nif = str(payload.get("nif", "")).strip().upper()
    modalidad_poliza = str(payload.get("modalidadPoliza", "Adeslas Premier (90%)")).strip()
    concepto = str(payload.get("conceptoFactura", "Consulta Especialista Externo")).strip()
    iban = str(payload.get("iban", "")).strip().upper().replace(" ", "")

    try:
        importe = float(payload.get("importeFactura", 0))
    except (TypeError, ValueError):
        importe = -1.0

    if not re.fullmatch(r"[0-9XYZ]\d{7}[A-Z]", nif):
        return (
            jsonify(
                {
                    "ok": False,
                    "errorCode": "INVALID_NIF",
                    "mensaje": "El NIF/NIE introducido no tiene un formato válido (ej. 12345678Z).",
                }
            ),
            400,
        )

    if importe <= 0:
        return (
            jsonify(
                {
                    "ok": False,
                    "errorCode": "INVALID_AMOUNT",
                    "mensaje": "El importe de la factura debe ser mayor que 0,00 €.",
                }
            ),
            400,
        )

    if not re.fullmatch(r"ES\d{22}", iban):
        return (
            jsonify(
                {
                    "ok": False,
                    "errorCode": "INVALID_IBAN",
                    "mensaje": "El código IBAN debe comenzar por ES seguido de 22 dígitos numéricos.",
                }
            ),
            400,
        )

    porcentaje = 0.90 if "premier" in modalidad_poliza.lower() or "90" in modalidad_poliza else 0.80
    importe_reembolsado = round(importe * porcentaje, 2)
    expediente = f"RMB-2026-{random.randint(10000, 99999)}"

    registro = {
        "expediente": expediente,
        "nif": nif,
        "modalidadPoliza": modalidad_poliza,
        "conceptoFactura": concepto,
        "importeFactura": round(importe, 2),
        "porcentajeCobertura": int(porcentaje * 100),
        "importeEstimadoReembolso": importe_reembolsado,
        "ibanAbono": f"{iban[:4]} **** **** **** {iban[-4:]}",
        "estado": "EN_TRAMITACION_ABONO",
        "plazoEstimadoDias": 5,
        "fechaRegistro": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    REEMBOLSOS_REGISTRADOS.append(registro)
    return jsonify({"ok": True, "reembolso": registro}), 201


@app.route("/api/v1/auth/login", methods=["POST"])
def api_login_cliente():
    payload = request.get_json(silent=True) or {}
    nif = str(payload.get("nif", "")).strip().upper()
    password = str(payload.get("password", "")).strip()

    cliente = CLIENTES_DB.get(nif)
    if not cliente or cliente["password"] != password:
        return (
            jsonify(
                {
                    "ok": False,
                    "errorCode": "AUTH_INVALID_CREDENTIALS",
                    "mensaje": "NIF/NIE o contraseña incorrectos. Para pruebas QAOps utilice 12345678Z / Adeslas2026!.",
                }
            ),
            401,
        )

    perfil_publico = {k: v for k, v in cliente.items() if k != "password"}
    return jsonify({"ok": True, "cliente": perfil_publico})


@app.route("/api/v1/citas", methods=["POST"])
def api_crear_cita():
    payload = request.get_json(silent=True) or {}
    especialidad = str(payload.get("especialidad", "Medicina General")).strip()
    modalidad = str(payload.get("modalidadCita", "Videoconsulta Inmediata")).strip()
    motivo = str(payload.get("motivoConsulta", "")).strip()
    telefono = str(payload.get("telefonoContacto", "600123456")).strip()

    if not motivo:
        return (
            jsonify(
                {
                    "ok": False,
                    "errorCode": "MISSING_REASON",
                    "mensaje": "Por favor indique brevemente el motivo de la orientación o videoconsulta médica.",
                }
            ),
            400,
        )

    codigo_cita = f"CIT-2026-{random.randint(10000, 99999)}"
    cita = {
        "codigoCita": codigo_cita,
        "especialidad": especialidad,
        "modalidadCita": modalidad,
        "motivoConsulta": motivo,
        "telefonoContacto": telefono,
        "facultativoAsignado": "Dra. Patricia Navarro Solís (Colegiada Nº 28/49102)",
        "salaVirtualUrl": f"https://saluddigital.segurcaixaadeslas.es/sala/{codigo_cita}",
        "estado": "CONFIRMADA",
    }
    CITAS_REGISTRADAS.append(cita)
    return jsonify({"ok": True, "cita": cita}), 201


# ---------------------------------------------------------------------------
# Endpoints ALM & QAOps Telemetry (Jira Xray / TestLink / Redmine / JMeter AI)
# ---------------------------------------------------------------------------


@app.route("/api/v1/alm/backlog", methods=["GET"])
def api_alm_backlog():
    data = load_alm_backlog()
    return jsonify(
        {
            "ok": True,
            "backlog": data,
            "seleniumReport": SELENIUM_LATEST_REPORT,
            "jmeterReport": JMETER_LATEST_REPORT,
            "executions": EXECUTION_HISTORY,
        }
    )


@app.route("/api/v1/qaops/test-runs", methods=["POST"])
def api_update_test_runs():
    """
    Recibe resultados de ejecución desde Pytest/Selenium o desde el Servidor MCP de Selenium
    y actualiza en vivo el estado de los casos de prueba en el Backlog ALM y en SELENIUM_LATEST_REPORT.
    """
    payload = request.get_json(silent=True) or {}
    results = payload.get("results", [])
    if isinstance(payload, dict) and "key" in payload and not results:
        results = [payload]

    alm_data = load_alm_backlog()
    updated_keys = []
    total_ms = 0
    passed_cnt = 0
    failed_cnt = 0

    for res in results:
        tc_key = res.get("key")
        new_status = res.get("status", "PASSED").upper()
        duration_ms = res.get("durationMs")
        if new_status == "PASSED":
            passed_cnt += 1
        else:
            failed_cnt += 1
        if duration_ms is not None:
            total_ms += int(duration_ms)

        for tc in alm_data.get("testCases", []):
            if tc.get("key") == tc_key or tc.get("testLinkId") == tc_key:
                tc["status"] = new_status
                if duration_ms is not None:
                    tc["lastExecutionTimeMs"] = int(duration_ms)
                updated_keys.append(tc["key"])

        for s_tc in SELENIUM_LATEST_REPORT.get("testCasesDetail", []):
            if s_tc.get("key") == tc_key or s_tc.get("testLinkId") == tc_key:
                s_tc["status"] = new_status
                if duration_ms is not None:
                    s_tc["durationMs"] = int(duration_ms)

    if updated_keys:
        save_alm_backlog(alm_data)
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        SELENIUM_LATEST_REPORT["timestamp"] = now_str
        if len(results) >= 5:
            SELENIUM_LATEST_REPORT["totalDurationMs"] = total_ms
            SELENIUM_LATEST_REPORT["passed"] = passed_cnt
            SELENIUM_LATEST_REPORT["failed"] = failed_cnt

        EXECUTION_HISTORY.insert(
            0,
            {
                "execKey": f"SCA-EXEC-2026-{100 + len(EXECUTION_HISTORY) + 1}",
                "buildName": (
                    f"Build #{100 + len(EXECUTION_HISTORY) + 1} · "
                    + (
                        "Suite Pytest + Selenium POM (E2E)"
                        if len(results) >= 5
                        else f"Sincronización Puntual ({', '.join(updated_keys)})"
                    )
                ),
                "runner": payload.get("runner", "Pytest + Selenium WebDriver / MCP Agent"),
                "environment": "Local Simulation (127.0.0.1:8080)",
                "testsScope": f"{len(updated_keys)} caso(s): {', '.join(updated_keys[:4])}{'...' if len(updated_keys) > 4 else ''}",
                "passed": passed_cnt,
                "failed": failed_cnt,
                "durationMs": total_ms or 550,
                "status": "PASSED" if failed_cnt == 0 else "FAILED",
                "timestamp": now_str,
            },
        )

    return jsonify({"ok": True, "updatedTestCases": updated_keys, "totalUpdated": len(updated_keys)})


@app.route("/api/v1/qaops/jmeter-report", methods=["POST"])
def api_update_jmeter_report():
    global JMETER_LATEST_REPORT
    payload = request.get_json(silent=True) or {}
    if payload:
        JMETER_LATEST_REPORT.update(payload)
        EXECUTION_HISTORY.insert(
            0,
            {
                "execKey": f"SCA-EXEC-2026-{100 + len(EXECUTION_HISTORY) + 1}",
                "buildName": f"Build #{100 + len(EXECUTION_HISTORY) + 1} · Performance Gate JMeter IA",
                "runner": "JMeter AI Assistant (ai_jmeter_assistant.py)",
                "environment": f"Local Simulation ({JMETER_LATEST_REPORT.get('totalSamples', 60)} muestras)",
                "testsScope": f"SCA-TC-011..012 (P95 = {JMETER_LATEST_REPORT.get('p95Ms')}ms, Apdex = {JMETER_LATEST_REPORT.get('apdex')})",
                "passed": 2 if JMETER_LATEST_REPORT.get("slaStatus") == "PASSED" else 0,
                "failed": 0 if JMETER_LATEST_REPORT.get("slaStatus") == "PASSED" else 2,
                "durationMs": int(float(JMETER_LATEST_REPORT.get("p99Ms", 120)) * 12),
                "status": JMETER_LATEST_REPORT.get("slaStatus", "PASSED"),
                "timestamp": JMETER_LATEST_REPORT.get("timestamp"),
            },
        )
    return jsonify({"ok": True, "jmeterReport": JMETER_LATEST_REPORT})


@app.route("/api/v1/qaops/screenshot/<filename>", methods=["GET"])
def api_get_screenshot(filename: str):
    safe_name = Path(filename).name
    img_path = PROJECT_ROOT / "selenium-qaops" / "reports" / safe_name
    if img_path.exists():
        return send_file(img_path, mimetype="image/png")
    return jsonify({"ok": False, "error": "Screenshot no encontrado"}), 404


@app.route("/api/v1/qaops/trigger-selenium", methods=["POST"])
def api_trigger_selenium():
    """Lanza en vivo el Self-Test del Servidor MCP y la suite Pytest + Selenium desde el Dashboard ALM."""
    t0 = time.perf_counter()
    rc_mcp = subprocess.call(
        [sys.executable, str(PROJECT_ROOT / "mcp-selenium-server" / "server.py"), "--selftest"],
        cwd=str(PROJECT_ROOT),
    )
    rc_pytest = subprocess.call(
        [sys.executable, "-m", "pytest", "selenium-qaops/tests/test_servicios_clientes_e2e.py", "-q"],
        cwd=str(PROJECT_ROOT),
    )
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    return jsonify(
        {
            "ok": rc_mcp == 0 and rc_pytest == 0,
            "mcpExitCode": rc_mcp,
            "pytestExitCode": rc_pytest,
            "totalElapsedMs": elapsed_ms,
            "seleniumReport": SELENIUM_LATEST_REPORT,
        }
    )


@app.route("/api/v1/qaops/trigger-jmeter", methods=["POST"])
def api_trigger_jmeter():
    """Lanza en vivo la prueba de carga y análisis cognitivo JMeter IA desde el Dashboard ALM."""
    t0 = time.perf_counter()
    rc_jm = subprocess.call(
        [sys.executable, str(PROJECT_ROOT / "jmeter-ai" / "ai_jmeter_assistant.py"), "--vus", "12", "--iterations", "5"],
        cwd=str(PROJECT_ROOT),
    )
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    return jsonify(
        {
            "ok": rc_jm == 0,
            "exitCode": rc_jm,
            "totalElapsedMs": elapsed_ms,
            "jmeterReport": JMETER_LATEST_REPORT,
        }
    )


@app.route("/api/v1/alm/export/<fmt>", methods=["GET"])
def api_export_alm(fmt: str):
    fmt = fmt.lower()
    if fmt == "jira-xray":
        return send_file(ALM_JSON_PATH, as_attachment=True, download_name="backlog_xray_export.json")
    if fmt == "testlink":
        return send_file(TESTLINK_XML_PATH, as_attachment=True, download_name="segurcaixa_testplan_testlink.xml")
    if fmt == "redmine":
        return send_file(REDMINE_CSV_PATH, as_attachment=True, download_name="redmine_issues_backlog.csv")
    return jsonify({"ok": False, "error": "Formato no soportado. Use jira-xray, testlink o redmine."}), 404


if __name__ == "__main__":
    port = int(os.environ.get("ADESLAS_PORT", "8080"))
    app.run(host="127.0.0.1", port=port, debug=False)
