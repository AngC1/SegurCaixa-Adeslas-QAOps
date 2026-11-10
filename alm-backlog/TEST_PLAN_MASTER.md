# Master Test Plan (QAOps) — Portal Servicios para Clientes SegurCaixa Adeslas

- **Identificador del Plan**: `SCA-TP-2026-Q4`
- **Unidad Responsable**: Práctica de QAOps & Continuous Testing — **Ayesa Digital (BFSI)**
- **Objeto bajo Prueba (SUT)**: Portal `/servicios-para-clientes` de SegurCaixa Adeslas (`https://www.segurcaixaadeslas.es/servicios-para-clientes` / Simulación local `http://127.0.0.1:8080/servicios-para-clientes`)
- **Estándar de Referencia**: ISO/IEC/IEEE 29119 & ISTQB Agile QAOps

---

## 1. Alcance y Objetivos del Plan de Pruebas

Certificar de forma continua y automatizada los flujos críticos de negocio disponibles en el portal **Servicios para Clientes** de SegurCaixa Adeslas:

1. **Cuadro Médico y Urgencias 24h (`SCA-EP-01`)**: Búsqueda multicriterio por provincia, especialidad médica, modalidad de póliza (Plena Plus, Plena Vital, Seniors, Muface/Isfas) y filtrado de centros con cita online.
2. **Autorizaciones Médicas Online (`SCA-EP-02`)**: Validación de numeración de tarjeta sanitaria Adeslas (`8000...`), aprobación automática de actos estándar (`AUT-2026-XXXXX`) y derivación a inspección médica en pruebas complejas (Genética).
3. **Reembolso de Gastos Médicos (`SCA-EP-03`)**: Validación de NIF/IBAN y motor de cálculo de cobertura (90% Adeslas Premier, 80% Adeslas Extra).
4. **Área Cliente y Salud Digital (`SCA-EP-04`)**: Autenticación segura, visualización de Tarjeta Digital y reserva de Videoconsulta Médica.
5. **Rendimiento y Resiliencia (`SCA-EP-05`)**: Certificación de SLAs bajo concurrencia mediante **JMeter asistido por IA**.

---

## 2. Arquitectura del Stack QAOps de Ayesa Digital

```
┌───────────────────────────────────────────────────────────────────────────┐
│                 AYESA DIGITAL QAOPS CONTINUOUS PIPELINE                   │
├───────────────────────┬──────────────────────────┬────────────────────────┤
│  Agente IA + MCP      │  Automatización E2E      │  Performance & Load    │
│  Selenium MCP Server  │  Pytest + Selenium POM   │  JMeter 5.6 + AI Agent │
│  (Self-Healing DOM)   │  (Chrome/Edge Headless)  │  (JMX + JTL Analyzer)  │
└───────────┬───────────┴────────────┬─────────────┴───────────┬────────────┘
            │                        │                         │
            ▼                        ▼                         ▼
┌───────────────────────────────────────────────────────────────────────────┐
│     SUT: Simulador Portal SegurCaixa Adeslas (/servicios-para-clientes)   │
│     API REST (/api/v1/cuadro-medico, /autorizaciones, /reembolsos, ...)   │
└────────────────────────────────────┬──────────────────────────────────────┘
                                     │ Telemetría en Tiempo Real
                                     ▼
┌───────────────────────────────────────────────────────────────────────────┐
│        Hub ALM Unificado (/alm-dashboard): Jira+Xray | TestLink | Redmine │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Matriz de Trazabilidad (Jira Xray / TestLink / Redmine / Automatización)

| ID Jira Xray | ID TestLink | ID Redmine | Historia | Caso de Prueba | Tipo | Script Automatizado | SLA / Criterio |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SCA-TC-001` | `TL-SCA-101` | `#4011` | `SCA-US-101` | Renderizado del catálogo de Servicios para Clientes | E2E UI | `test_tc001_catalogo_servicios_clientes` | Carga < 1.5s |
| `SCA-TC-002` | `TL-SCA-102` | `#4012` | `SCA-US-101` | Búsqueda Cuadro Médico (Madrid + Cardiología) | E2E UI | `test_tc002_busqueda_cuadro_medico_madrid_cardiologia` | >= 1 centro devuelto |
| `SCA-TC-003` | `TL-SCA-103` | `#4013` | `SCA-US-101` | Búsqueda Urgencias 24h con póliza Muface | E2E UI | `test_tc003_busqueda_urgencias_muface` | Filtro exacto Muface |
| `SCA-TC-004` | `TL-SCA-104` | `#4014` | `SCA-US-102` | Solicitud exitosa de Autorización (Resonancia) | E2E UI | `test_tc004_solicitud_autorizacion_exitosa` | Estado `AUTORIZADA` |
| `SCA-TC-005` | `TL-SCA-105` | `#4015` | `SCA-US-102` | Validación negativa de tarjeta Adeslas inválida | E2E UI | `test_tc005_autorizacion_tarjeta_invalida` | HTTP 400 + Alerta UI |
| `SCA-TC-006` | `TL-SCA-106` | `#4016` | `SCA-US-102` | Autorización Estudio Genético a Revisión Médica | API / E2E | `test_tc006_autorizacion_revision_medica` | Estado `PENDIENTE_REVISION_MEDICA` |
| `SCA-TC-007` | `TL-SCA-107` | `#4017` | `SCA-US-103` | Reembolso Póliza Adeslas Premier (cálculo 90%) | E2E UI | `test_tc007_reembolso_premier_calculo_90` | Abono = 90% factura |
| `SCA-TC-008` | `TL-SCA-108` | `#4018` | `SCA-US-103` | Validación de IBAN incorrecto en Reembolso | E2E UI | `test_tc008_reembolso_iban_invalido` | Rechazo formato IBAN |
| `SCA-TC-009` | `TL-SCA-109` | `#4019` | `SCA-US-104` | Login Área Cliente y Tarjeta Digital Adeslas | E2E UI | `test_tc009_login_area_cliente_tarjeta_digital` | Tarjeta visible |
| `SCA-TC-010` | `TL-SCA-110` | `#4020` | `SCA-US-105` | Reserva de Videoconsulta de Orientación Médica | E2E UI | `test_tc010_reserva_videoconsulta_medica` | Código `CIT-2026-XXXXX` |
| `SCA-TC-011` | `TL-SCA-111` | `#4021` | `SCA-US-106` | Carga JMeter AI - Buscador Cuadro Médico | Performance | `TG01_Busqueda_Cuadro_Medico` | P95 < 450ms, Error < 1% |
| `SCA-TC-012` | `TL-SCA-112` | `#4022` | `SCA-US-106` | Estrés JMeter AI - Pico de Autorizaciones | Performance | `TG02_Tramite_Autorizaciones` | Apdex >= 0.90 |

---

## 4. Criterios de Entrada, Salida y Quality Gates (CI/CD)

- **Quality Gate 1 (Smoke & API Contract)**: 100% de endpoints `/api/v1/*` respondiendo con latencia media < 150ms.
- **Quality Gate 2 (Selenium E2E + MCP Self-Healing)**: 100% de casos críticos (`Priority = Highest/High`) en estado `PASSED`.
- **Quality Gate 3 (JMeter AI Performance Gate)**:
  - Percentil 95 (`P95`) global <= `450 ms`.
  - Tasa de error (`Error %`) <= `1.0%`.
  - Índice de satisfacción `Apdex` >= `0.90`.
