"""
Suite Automatizada E2E (Selenium WebDriver + Pytest) para SegurCaixa Adeslas (/servicios-para-clientes).
Mapeada 1:1 con el Backlog ALM en Jira Xray (SCA-TC-001..010), TestLink (TL-SCA-101..110) y Redmine (#4011..4020).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pages.servicios_clientes_page import ServiciosClientesPage


@pytest.mark.xray("SCA-TC-001")
def test_tc001_catalogo_servicios_clientes(driver, base_url):
    """SCA-TC-001 / TL-SCA-101: Renderizado del catálogo de Servicios para Clientes y KPIs."""
    page = ServiciosClientesPage(driver, base_url).open()
    assert "servicios de salud" in page.get_hero_title().lower()
    assert page.get_service_cards_count() == 6


@pytest.mark.xray("SCA-TC-002")
def test_tc002_busqueda_cuadro_medico_madrid_cardiologia(driver, base_url):
    """SCA-TC-002 / TL-SCA-102: Búsqueda en Cuadro Médico por Provincia (Madrid) y Especialidad (Cardiología)."""
    page = ServiciosClientesPage(driver, base_url).open()
    total = page.buscar_cuadro_medico(provincia="Madrid", especialidad="Cardiología")
    assert total >= 2


@pytest.mark.xray("SCA-TC-003")
def test_tc003_busqueda_urgencias_muface(driver, base_url):
    """SCA-TC-003 / TL-SCA-103: Búsqueda de Centros de Urgencias 24h con filtro de póliza Muface / Isfas."""
    page = ServiciosClientesPage(driver, base_url).open()
    total = page.buscar_cuadro_medico(especialidad="Urgencias 24h", poliza="Muface / Isfas")
    assert total >= 2


@pytest.mark.xray("SCA-TC-004")
def test_tc004_solicitud_autorizacion_exitosa(driver, base_url):
    """SCA-TC-004 / TL-SCA-104: Solicitud exitosa de Autorización Médica automática (Resonancia Magnética)."""
    page = ServiciosClientesPage(driver, base_url).open()
    resultado = page.solicitar_autorizacion(
        num_tarjeta="8000123456789012",
        tipo_acto_visible="Resonancia Magnética Nuclear (RMN)",
        prescripcion="RX-99281",
        centro="Hospital Ruber Internacional",
    )
    assert "AUTORIZADA" in resultado
    assert "AUT-2026-" in resultado


@pytest.mark.xray("SCA-TC-005")
def test_tc005_autorizacion_tarjeta_invalida(driver, base_url):
    """SCA-TC-005 / TL-SCA-105: Validación negativa de Autorización con número de tarjeta Adeslas inválido."""
    page = ServiciosClientesPage(driver, base_url).open()
    resultado = page.solicitar_autorizacion(
        num_tarjeta="12345",
        tipo_acto_visible="TAC / Escáner Diagnóstico",
        prescripcion="TAC-1102",
        centro="Hospital Quirónsalud",
    )
    assert "Error en la validación" in resultado
    assert "12 y 16 dígitos" in resultado


@pytest.mark.xray("SCA-TC-006")
def test_tc006_autorizacion_revision_medica(base_url):
    """SCA-TC-006 / TL-SCA-106: Autorización de Estudio Genético derivada a Revisión Médica Facultativa."""
    res = requests.post(
        f"{base_url}/api/v1/autorizaciones",
        json={
            "numTarjeta": "8000123456789012",
            "tipoActo": "Estudio Genético Oncológico",
            "codigoPrescripcion": "GEN-55019",
            "centroMedico": "Centro Médico Teknon",
        },
        timeout=5,
    )
    assert res.status_code == 201
    data = res.json()
    assert data["ok"] is True
    assert data["autorizacion"]["estado"] == "PENDIENTE_REVISION_MEDICA"


@pytest.mark.xray("SCA-TC-007")
def test_tc007_reembolso_premier_calculo_90(driver, base_url):
    """SCA-TC-007 / TL-SCA-107: Registro de Reembolso de Gastos Médicos (Póliza Adeslas Premier - 90% cobertura)."""
    page = ServiciosClientesPage(driver, base_url).open()
    resultado = page.solicitar_reembolso(
        nif="12345678Z",
        modalidad_visible="Adeslas Premier (90% Cobertura)",
        importe="250.00",
        iban="ES9121000418450200051332",
    )
    assert "RMB-2026-" in resultado
    assert "225.00 EUR" in resultado


@pytest.mark.xray("SCA-TC-008")
def test_tc008_reembolso_iban_invalido(driver, base_url):
    """SCA-TC-008 / TL-SCA-108: Validación de IBAN incorrecto en solicitud de Reembolso."""
    page = ServiciosClientesPage(driver, base_url).open()
    resultado = page.solicitar_reembolso(
        nif="12345678Z",
        modalidad_visible="Adeslas Extra (80% Cobertura)",
        importe="120.00",
        iban="ES1234",
    )
    assert "Error en solicitud de reembolso" in resultado
    assert "IBAN" in resultado


@pytest.mark.xray("SCA-TC-009")
def test_tc009_login_area_cliente_tarjeta_digital(driver, base_url):
    """SCA-TC-009 / TL-SCA-109: Acceso al Área Cliente y visualización de Tarjeta Digital Adeslas."""
    page = ServiciosClientesPage(driver, base_url).open()
    resultado = page.login_area_cliente("12345678Z", "Adeslas2026!")
    assert "Carlos Martínez Gómez" in resultado
    assert "POL-SCA-908122" in resultado
    assert "8000123456789012" in resultado


@pytest.mark.xray("SCA-TC-010")
def test_tc010_reserva_videoconsulta_medica(driver, base_url):
    """SCA-TC-010 / TL-SCA-110: Reserva de Videoconsulta de Orientación Médica 24h."""
    page = ServiciosClientesPage(driver, base_url).open()
    resultado = page.reservar_videoconsulta(
        especialidad_visible="Medicina General (24h)",
        motivo="Consulta preventiva sobre resultados de analítica anual",
    )
    assert "CIT-2026-" in resultado
    assert "Dra. Patricia Navarro Solís" in resultado
