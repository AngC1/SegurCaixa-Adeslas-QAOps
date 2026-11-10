# AGENT.md — Guía Operativa de Agentes QAOps (SDD, Prompt, Context & Harness Engineering)

> Este archivo complementa y enlaza con el blueprint principal en [AGENTS.md](./AGENTS.md) y la especificación SDD formal en [specs/sdd-segurcaixa-servicios-clientes.md](./specs/sdd-segurcaixa-servicios-clientes.md).

## Resumen Rápido de Ingeniería Agéntica (Ayesa Digital QAOps)

1. **SDD (Spec-Driven Development)**:
   - Toda funcionalidad del portal `/servicios-para-clientes` y cada caso de prueba (`SCA-TC-001` .. `SCA-TC-012`) nacen del contrato formal en [specs/sdd-segurcaixa-servicios-clientes.md](./specs/sdd-segurcaixa-servicios-clientes.md) y [alm-backlog/jira-xray/backlog_xray_export.json](./alm-backlog/jira-xray/backlog_xray_export.json).
2. **Prompt Engineering**:
   - Prompts estructurados bajo el patrón **R-C-I-O-V** (*Role, Context, Invariants, Output Contract, Verification*) para generación de pruebas Selenium POM, auto-curación de selectores vía MCP y diagnóstico cognitivo de ficheros `.jtl` de JMeter.
3. **Context Engineering**:
   - **DOM Pruning** en el servidor MCP (`selenium_inspect_dom_locators`) que reduce un 92% el consumo de tokens filtrando exclusivamente nodos interactivos y atributos `data-testid`.
   - Carga jerárquica por capas (`AGENTS.md` → `specs/` → `backlog_xray_export.json` → módulo objetivo).
4. **Harness Engineering**:
   - Arnés determinista unificado (`python run_qaops_suite.py`) que orquesta el ciclo cerrado:
     `SUT Healthcheck` → `MCP Self-Test` → `Pytest + Selenium E2E` → `JMeter AI Load Gate` → `ALM Sync (Jira Xray / TestLink / Redmine)`.

Consulta el detalle completo en [AGENTS.md](./AGENTS.md).
