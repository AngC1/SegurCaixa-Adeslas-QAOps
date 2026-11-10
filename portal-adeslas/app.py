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
    "scenario": "Campaña Salud Invierno - Servicios para Clientes (50 VUs)",
    "totalSamples": 180,
    "throughputRps": 42.6,
    "avgResponseMs": 68.4,
    "p90Ms": 134.0,
    "p95Ms": 178.5,
    "p99Ms": 292.0,
    "errorRatePct": 0.0,
    "apdex": 0.97,
    "slaStatus": "PASSED",
    "aiInsights": [
        "SLA Global cumplido holgadamente: P95 = 178.5 ms frente al umbral máximo permitido de 450 ms.",
        "El endpoint /api/v1/cuadro-medico mantiene una latencia P95 de 84 ms gracias a la indexación en memoria.",
        "Se observa un incremento de latencia (+140 ms) en /api/v1/autorizaciones cuando el tipo de acto es 'Estudio Genético Oncológico' (validación de baremos complejos). Recomendación IA: cachear catálogo de baremos en Redis.",
    ],
    "endpoints": [
        {"label": "GET /api/v1/cuadro-medico", "samples": 80, "avgMs": 45.2, "p95Ms": 84.0, "errorPct": 0.0},
        {"label": "POST /api/v1/autorizaciones", "samples": 50, "avgMs": 96.8, "p95Ms": 215.0, "errorPct": 0.0},
        {"label": "POST /api/v1/reembolsos", "samples": 50, "avgMs": 77.1, "p95Ms": 148.0, "errorPct": 0.0},
    ],
}


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
    )


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
    return jsonify({"ok": True, "backlog": data, "jmeterReport": JMETER_LATEST_REPORT})


@app.route("/api/v1/qaops/test-runs", methods=["POST"])
def api_update_test_runs():
    """
    Recibe resultados de ejecución desde Pytest/Selenium o desde el Servidor MCP de Selenium
    y actualiza en vivo el estado de los casos de prueba en el Backlog ALM.
    """
    payload = request.get_json(silent=True) or {}
    results = payload.get("results", [])
    if isinstance(payload, dict) and "key" in payload and not results:
        results = [payload]

    alm_data = load_alm_backlog()
    updated_keys = []
    for res in results:
        tc_key = res.get("key")
        new_status = res.get("status", "PASSED").upper()
        duration_ms = res.get("durationMs")
        for tc in alm_data.get("testCases", []):
            if tc.get("key") == tc_key or tc.get("testLinkId") == tc_key:
                tc["status"] = new_status
                if duration_ms is not None:
                    tc["lastExecutionTimeMs"] = int(duration_ms)
                updated_keys.append(tc["key"])

    if updated_keys:
        save_alm_backlog(alm_data)

    return jsonify({"ok": True, "updatedTestCases": updated_keys, "totalUpdated": len(updated_keys)})


@app.route("/api/v1/qaops/jmeter-report", methods=["POST"])
def api_update_jmeter_report():
    global JMETER_LATEST_REPORT
    payload = request.get_json(silent=True) or {}
    if payload:
        JMETER_LATEST_REPORT.update(payload)
    return jsonify({"ok": True, "jmeterReport": JMETER_LATEST_REPORT})


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
