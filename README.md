# SegurCaixa Adeslas (`/servicios-para-clientes`) — Stack QAOps de Ayesa Digital

Simulación integral del portal **[Servicios para Clientes de SegurCaixa Adeslas](https://www.segurcaixaadeslas.es/servicios-para-clientes)** junto con el ecosistema de ingeniería de calidad continua (**QAOps**) de **Ayesa Digital**:

1. **Portal Web + API REST Simulada (`portal-adeslas/`)**:
   - Flujos reales de **Cuadro Médico y Urgencias 24h**, **Autorizaciones Médicas Online**, **Reembolso de Facturas (80%/90%)**, **Área Cliente + Tarjeta Digital** y **Videoconsulta Médica 24h**.
2. **Hub ALM Unificado (`alm-backlog/` y `/alm-dashboard`)**:
   - Simulación interactiva con vistas conmutables para **Jira + Xray**, **TestLink / TestPlan** y **Redmine**, además de exportaciones oficiales listas para importar (`JSON`, `XML`, `CSV`) y el **Master Test Plan (`TEST_PLAN_MASTER.md`)**.
3. **Automatización E2E Selenium + Self-Healing POM (`selenium-qaops/`)**:
   - Suite **Pytest + Selenium WebDriver** (`SCA-TC-001` a `SCA-TC-010`) con localizadores auto-reparables y reporte automático en vivo al Hub ALM.
4. **Servidor MCP de Selenium para Agentes IA (`mcp-selenium-server/`)**:
   - Servidor **Model Context Protocol (JSON-RPC 2.0 stdio)** que expone herramientas para abrir sesión, navegar, inspeccionar selectores resilientes del DOM, ejecutar flujos de SegurCaixa Adeslas y sincronizar ejecuciones con Jira/TestLink/Redmine.
5. **JMeter Asistido por IA (`jmeter-ai/`)**:
   - Plan nativo Apache JMeter 5.6 (`segurcaixa_servicios_clientes.jmx`), datasets CSV y motor cognitivo `ai_jmeter_assistant.py` que ejecuta pruebas de carga concurrentes, genera ficheros `.jtl`, calcula `P50/P90/P95/P99` + `Apdex` y detecta cuellos de botella automáticamente.

---

## Estructura del Proyecto

```text
├── portal-adeslas/
│   ├── app.py                                  # Servidor Flask (Portal + API REST + Hub ALM)
│   └── templates/
│       ├── servicios_clientes.html             # Simulación UI /servicios-para-clientes
│       └── alm_dashboard.html                  # Dashboard interactivo Jira Xray / TestLink / Redmine / JMeter IA
├── alm-backlog/
│   ├── TEST_PLAN_MASTER.md                     # Plan de Pruebas Maestro ISO 29119 / ISTQB
│   ├── jira-xray/backlog_xray_export.json      # Épicas, Historias, Test Plan, Casos Xray (Gherkin) y Defectos
│   ├── testlink/segurcaixa_testplan_testlink.xml # Exportación jerárquica XML oficial para TestLink
│   └── redmine/redmine_issues_backlog.csv      # Backlog e Issues QA en formato CSV de Redmine
├── selenium-qaops/
│   ├── conftest.py                             # Fixtures WebDriver Headless + Hook de sincronización ALM
│   ├── pages/servicios_clientes_page.py        # Page Object Model con Self-Healing Locators
│   └── tests/test_servicios_clientes_e2e.py    # 10 Tests automatizados (SCA-TC-001 a SCA-TC-010)
├── mcp-selenium-server/
│   ├── server.py                               # Servidor MCP de Selenium (stdio + modo --selftest)
│   └── mcp_config.json                         # Configuración MCP para Antigravity / Claude / Cursor
├── jmeter-ai/
│   ├── ai_jmeter_assistant.py                  # Ejecutor concurrente JTL + Analizador IA de rendimiento
│   ├── plans/segurcaixa_servicios_clientes.jmx # Plan Apache JMeter 5.6 (3 Thread Groups)
│   ├── data/busquedas_cuadro_medico.csv        # Dataset parametrizado JMeter
│   └── results/                                # Ficheros .jtl e Informe IA en Markdown
├── ci-cd/
│   └── Jenkinsfile                             # Pipeline declarativo CI/CD QAOps
├── .github/workflows/ayesa-qaops-pipeline.yml  # Workflow GitHub Actions QAOps
└── run_qaops_suite.py                          # Orquestador E2E de toda la suite QAOps
```

---

## Ejecución Rápida

### 1. Ejecutar toda la Certificación QAOps en un solo comando
```powershell
python run_qaops_suite.py
```

### 2. Levantar el Portal SegurCaixa Adeslas y el Hub ALM para exploración interactiva
```powershell
python portal-adeslas/app.py
```
- **Portal Servicios para Clientes**: `http://127.0.0.1:8080/servicios-para-clientes`
- **Hub ALM (Jira Xray / TestLink / Redmine / JMeter IA)**: `http://127.0.0.1:8080/alm-dashboard`
