# AGENTS.md — Blueprint de Ingeniería Agéntica QAOps (Ayesa Digital · SegurCaixa Adeslas)

Este documento define las directrices operativas de **SDD (Spec-Driven Development)**, **Prompt Engineering**, **Context Engineering** y **Harness Engineering** para todos los agentes de IA (Antigravity, Claude Code, Cursor, GitHub Copilot Workspace y subagentes QAOps) que operan sobre el ecosistema de **SegurCaixa Adeslas (`/servicios-para-clientes`)**.

---

## 1. SDD — Specification-Driven Development (Desarrollo Guiado por Especificaciones)

En el modelo **QAOps de Ayesa Digital**, ningún código de aplicación ni script de prueba se escribe sin una especificación verificable previa. La especificación es la **fuente única de verdad (Single Source of Truth)** que conecta negocio, desarrollo y aseguramiento de calidad.

### 1.1 Pirámide de Especificación Ejecutable
1. **Especificación de Dominio y Negocio (`alm-backlog/jira-xray/backlog_xray_export.json`)**:
   - Define Épicas (`SCA-EP-01`..`05`) e Historias de Usuario (`SCA-US-101`..`106`) con criterios de aceptación explícitos y medibles.
2. **Especificación de Comportamiento BDD/Gherkin (`testCases[*].gherkin`)**:
   - Cada caso de prueba (`SCA-TC-001`..`SCA-TC-012`) declara formalmente `Given / When / Then`.
3. **Contratos de Interfaz y Reglas de Negocio (`specs/sdd-segurcaixa-servicios-clientes.md`)**:
   - **Cuadro Médico (`GET /api/v1/cuadro-medico`)**: Filtrado determinista por `provincia`, `especialidad`, `poliza` y `urgencias24h`.
   - **Autorizaciones (`POST /api/v1/autorizaciones`)**:
     - Invariante 1: `numTarjeta` cumple `^\d{12,16}$`. En caso contrario → `HTTP 400` (`INVALID_CARD_NUMBER`).
     - Invariante 2: Actos estándar → estado `AUTORIZADA` + código `AUT-2026-XXXXX`.
     - Invariante 3: Actos complejos (`Estudio Genético Oncológico`) → estado `PENDIENTE_REVISION_MEDICA`.
   - **Reembolsos (`POST /api/v1/reembolsos`)**:
     - Invariante 1: `nif` cumple `^[0-9XYZ]\d{7}[A-Z]$`, `iban` cumple `^ES\d{22}$`, `importeFactura > 0`.
     - Invariante 2: Cálculo exacto de cobertura: **90%** para `Adeslas Premier` y **80%** para `Adeslas Extra`.
4. **Especificación No Funcional / SLAs (`alm-backlog/TEST_PLAN_MASTER.md`)**:
   - Percentil 95 (`P95`) `< 450 ms`, tasa de error `<= 1.0%`, e índice `Apdex >= 0.90`.

### 1.2 Regla de Oro SDD para el Agente
- Antes de modificar cualquier endpoint en `portal-adeslas/app.py` o cualquier flujo UI en `portal-adeslas/templates/servicios_clientes.html`, el agente **DEBE**:
  1. Consultar la especificación en `specs/sdd-segurcaixa-servicios-clientes.md` y `alm-backlog/jira-xray/backlog_xray_export.json`.
  2. Mantener la trazabilidad 1:1 mediante el marcador `@pytest.mark.xray("SCA-TC-XXX")` en `selenium-qaops/tests/test_servicios_clientes_e2e.py`.
  3. Ejecutar el arnés de validación (`python run_qaops_suite.py`) para demostrar conformidad con la especificación.

---

## 2. Prompt Engineering — Arquitectura de Prompts para QAOps

Los prompts empleados por los agentes de pruebas funcionales y de rendimiento siguen el patrón **R-C-I-O-V (Role, Context, Invariants, Output Contract, Verification)**.

### 2.1 Prompt Maestro: Generación de Tests E2E Selenium desde Especificación SDD
```markdown
[ROLE]
Actúa como Ingeniero Principal de Automatización QAOps de Ayesa Digital especializado en sector asegurador salud (BFSI - SegurCaixa Adeslas).

[CONTEXT]
- SUT: http://127.0.0.1:8080/servicios-para-clientes
- Page Object: selenium-qaops/pages/servicios_clientes_page.py (usa find_healed() con prioridades: By.ID -> data-testid -> CSS)
- Fuente ALM: alm-backlog/jira-xray/backlog_xray_export.json

[INVARIANTS]
1. Todo test debe llevar el decorador @pytest.mark.xray("SCA-TC-XXX") y documentar su ID equivalente en TestLink (TL-SCA-XXX) y Redmine (#XXXX).
2. Prohibido usar time.sleep() arbitrarios en tests Pytest; utiliza WebDriverWait determinista a través del Page Object.
3. No acoplar los tests a clases visuales CSS; usar exclusivamente IDs semánticos o atributos data-testid.

[OUTPUT CONTRACT]
Genera código Python compatible con pytest >= 7.4 y selenium >= 4.20 que actualice automáticamente el Hub ALM mediante el hook pytest_sessionfinish.
```

### 2.2 Prompt Maestro: Auto-Curación de Localizadores (Self-Healing via MCP)
```markdown
[ROLE]
Eres el Agente de Auto-Curación (Self-Healing Locator Engine) conectado al servidor MCP `ayesa-selenium-qaops`.

[WORKFLOW]
1. Invoca la herramienta MCP `selenium_inspect_dom_locators` sobre la vista activa.
2. Compara el selector fallido con el catálogo de `id`, `dataTestId` y `labelOrText` devuelto por el DOM vivo.
3. Selecciona el candidato con mayor similitud semántica y actualiza la lista de tuplas en `find_healed([...])` dentro de `servicios_clientes_page.py`.
4. Ejecuta `selenium_execute_adeslas_flow` y `alm_sync_test_result` para certificar la reparación.
```

### 2.3 Prompt Maestro: Diagnóstico Cognitivo de Rendimiento (JMeter AI)
```markdown
[ROLE]
Actúa como Arquitecto SRE & Performance QAOps de Ayesa Digital analizando muestras JTL de Apache JMeter.

[TASK]
Analiza las distribuciones de latencia (P50, P90, P95, P99), el Throughput (req/s) y el Apdex (T = 180ms) de cada transacción del portal SegurCaixa Adeslas.
- Si un endpoint supera 1.5x la latencia media global (ej. validación de 'Estudio Genético Oncológico'), identifica la causa raíz arquitectónica, vincúlala con el defecto correspondiente en el Backlog (ej. `SCA-BUG-201`) y propón una mitigación concreta (caché Redis de baremos médicos, desacoplamiento asíncrono).
```

---

## 3. Context Engineering — Gestión Eficiente de Contexto para Agentes

Para maximizar la precisión del modelo y evitar la degradación por exceso de tokens (*Context Rot*), el proyecto implementa cuatro estrategias de **Context Engineering**:

### 3.1 Poda Semántica del DOM (DOM Pruning en el Servidor MCP)
- Enviar el HTML crudo de una página aseguradora a un LLM consume decenas de miles de tokens innecesarios.
- En [`SeleniumMcpController.inspect_dom_locators`](./mcp-selenium-server/server.py#L72-L99), el servidor MCP filtra únicamente nodos accionables (`button, input, select, a, [data-testid]`), limita la respuesta a un inventario estructurado JSON (`tag`, `id`, `dataTestId`, `recommendedCss`, `selfHealingFallbackCss`) y reduce el consumo de contexto en más de un **92%**.

### 3.2 Empaquetado de Contexto por Capas (Layered Context Retrieval)
Cuando un agente aborda una tarea en este repositorio, debe cargar el contexto en este orden estricto:
1. **Capa 0 (Índice y Reglas)**: `AGENTS.md` + `specs/sdd-segurcaixa-servicios-clientes.md` (~2k tokens).
2. **Capa 1 (Estado del Backlog y Contratos)**: `alm-backlog/jira-xray/backlog_xray_export.json` (~2.5k tokens).
3. **Capa 2 (Implementación Focalizada)**: Solo el módulo afectado (`portal-adeslas/app.py`, `selenium-qaops/pages/servicios_clientes_page.py`, o `jmeter-ai/ai_jmeter_assistant.py`).
4. **Capa 3 (Evidencia de Ejecución)**: Resumen estadístico en `jmeter-ai/results/AI_PERFORMANCE_REPORT.md` en lugar de leer miles de líneas crudas del fichero `.jtl`.

### 3.3 Sincronización Bidireccional de Estado (Shared State Memory)
- El archivo `alm-backlog/jira-xray/backlog_xray_export.json` y el endpoint `/api/v1/alm/backlog` actúan como **memoria persistente compartida** entre el agente de pruebas funcionales (Selenium/Pytest), el servidor MCP y el agente de rendimiento (JMeter AI).

---

## 4. Harness Engineering — Ingeniería del Arnés de Ejecución y Verificación

Un agente de IA es tan fiable como el **arnés (harness)** que ejecuta sus acciones, captura la telemetría y valida los resultados de forma determinista. Este proyecto incluye un arnés multicapa completo:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                   ARNÉS DE INGENIERÍA AGÉNTICA (HARNESS)                   │
│                                                                            │
│  1. Orchestration Harness (run_qaops_suite.py)                             │
│     ├─ Autodetección y arranque efímero del SUT (puerto 8080)              │
│     ├─ Secuenciación determinista de 4 puertas de calidad (Quality Gates)  │
│     └─ Teardown limpio garantizado (bloque try/finally)                    │
│                                                                            │
│  2. MCP Tool Harness (mcp-selenium-server/server.py)                       │
│     ├─ Protocolo JSON-RPC 2.0 sobre stdio + modo --selftest autónomo       │
│     ├─ Gestión segura del ciclo de vida WebDriver (Chrome -> fallback Edge)│
│     └─ Captura automática de evidencias PNG en selenium-qaops/reports/     │
│                                                                            │
│  3. Self-Healing UI Harness (selenium-qaops/conftest.py + POM)             │
│     ├─ Resolución multicandidato de selectores con registro de curación    │
│     └─ Hook pytest_runtest_makereport -> POST /api/v1/qaops/test-runs      │
│                                                                            │
│  4. Performance Evaluation Harness (jmeter-ai/ai_jmeter_assistant.py)      │
│     ├─ Generador concurrente de trazas .jtl compatibles con JMeter 5.6     │
│     └─ Evaluador matemático de SLAs (P95, Error %, Apdex) + Reporte ALM    │
└────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Comandos del Arnés de Verificación (Verification Loop)

| Nivel del Arnés | Comando de Ejecución | Qué Verifica (Quality Gate) |Tiempo Medio |
| :--- | :--- | :--- | :--- |
| **Arnés Completo (Full Gate)** | `python run_qaops_suite.py` | Levanta SUT + MCP Self-Test + 10 Tests Pytest Selenium + JMeter AI + Sincronización ALM (12/12 casos) | ~9 seg |
| **Arnés MCP (Tool Harness)** | `python mcp-selenium-server/server.py --selftest` | Verifica sesión Headless, extracción de 40 selectores DOM, flujos MCP y captura PNG | ~2.5 seg |
| **Arnés E2E Funcional** | `pytest selenium-qaops/tests/test_servicios_clientes_e2e.py -v` | Verifica `SCA-TC-001` a `SCA-TC-010` y publica resultados en Jira/Xray/TestLink | ~5.8 seg |
| **Arnés de Rendimiento IA** | `python jmeter-ai/ai_jmeter_assistant.py --vus 12 --iterations 5` | Verifica `SCA-TC-011` y `SCA-TC-012`, genera `.jtl`, calcula Apdex/P95 y escribe informe IA | ~1.5 seg |

### 4.2 Guardrails y Diseño Resiliente del Arnés
1. **Multi-Browser Fallback**: Tanto `conftest.py` como `mcp-selenium-server/server.py` intentan iniciar `Chrome Headless` y conmutan automáticamente a `Edge Headless` si el binario primario no está disponible.
2. **Dual-Engine JMeter Runner**: `ai_jmeter_assistant.py` soporta la invocación nativa del binario CLI `jmeter -n -t ...` (cuando `USE_NATIVE_JMETER=1`) e incorpora un motor concurrente `ThreadPoolExecutor` que emite ficheros `.jtl` idénticos a Apache JMeter para garantizar ejecución determinista en cualquier contenedor CI/CD sin dependencias externas pesadas.
3. **Idempotencia y Observabilidad**: Cada ejecución actualiza el estado real en `/api/v1/alm/backlog` y deja artefactos auditables en `selenium-qaops/reports/` y `jmeter-ai/results/`.
