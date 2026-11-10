# Presentación Ejecutiva: Capacidades en Adopción a la IA y Agentic QAOps en SegurCaixa Adeslas (SCA)

**Unidad**: Application Services & Digital Impact — **Ayesa Digital**  
**Contacto**: Ángel Carrasco (`adcarrasco@ayesa-digital.com`)  
**Formatos generados en esta carpeta**:
- 📊 **PowerPoint Editable (`.pptx`)**: [`Ayesa_Digital_QAOps_SegurCaixa_Adeslas_SCA.pptx`](./Ayesa_Digital_QAOps_SegurCaixa_Adeslas_SCA.pptx) (12 diapositivas 16:9 con diseño corporativo Ayesa Digital)
- 🌐 **Deck Web Interactivo (`.html` / `/presentacion`)**: [`index.html`](./index.html) (`http://127.0.0.1:8080/presentacion`)

---

## Estructura de Diapositivas (Slide-by-Slide)

### Slide 1 · Portada
- **Título**: Capacidades en Adopción a la IA en SegurCaixa Adeslas (SCA) — Aplicado al Desarrollo de SW, DevOps, DevSecOps y AI-Driven QAOps.
- **Subtítulo**: *Platform Engineering & SDD, Prompt, Context, Harness & Loop Engineering*.
- **Demostrador**: Incluye PoC real ejecutable de `/servicios-para-clientes` + Servidor MCP de Selenium + JMeter asistido por IA + Hub ALM Unificado.

---

### Slide 2 · [01] Ayesa Digital — ¿Quiénes Somos? y Propuesta de Valor
- **Escala Global**: Top 5 de los servicios TI en España | **580 M€** cifra de negocio | **11.000+ profesionales** en 10 países | 45 nacionalidades y +40 disciplinas.
- **Liderazgo en Satisfacción**: **#1 en el estudio Whitelane Research & Eraneos 2026** con un **86%** de satisfacción general.
- **Acreditaciones**: **CMMI Nivel 5**, **ENS Categoría Alta**, **ISO 27001 / 42001 (AI Act)** e **ISO 22301**.
- **Experiencia BFSI y Global**: SegurCaixa Adeslas, CaixaBank, BBVA, Santander, Kutxabank, Mapfre, Banco de España, Iberdrola (`-40%` incidencias críticas, `+35%` velocidad), L'Oréal EMEA (`-28%` OPEX, `+50%` velocidad).

---

### Slide 3 · [02] Diagnóstico Inicial en SCA: De Licencias a Productividad Medible
- **Contexto de Mercado**:
  - **75%** de los CIOs afirma que la deuda técnica limita su innovación (*Gartner*).
  - **48%** de iniciativas digitales no alcanza sus objetivos sin gobierno (*IDC*).
  - **70%** del presupuesto TI se destina a mantener sistemas existentes (*Forrester*).
- **Adopción Asimétrica en SCA (AS-IS)**:
  - `Python & Data Teams`: **78%** (Alta adopción).
  - `QA & Testing`: **44%** (Potencial moderado; automatización aislada y alta dependencia de UAT manual).
  - `SAP / ERP & Legacy`: **22%** (Oportunidad crítica).
- **Los 4 Refuerzos de nuestra Propuesta v2.0 (TO-BE)**:
  1. **SLAs por fase del SDLC** calibrados con datos históricos.
  2. **Modelo de gobierno multiproveedor** con perfiles nominados.
  3. **ROI cuantificado** por bloque de actividad (**Service Value Framework - SVF**).
  4. **Estrategia de implantación incremental** con resultados visibles en Semana 6 (Dashboard AXIA) y Semana 8 (primer informe CMR real).

---

### Slide 4 · [02] Solución Integral en 3 Servicios Interconectados (Agent-First)
1. **Servicio Especial 1: Oficina OCM & Gobierno**:
   - Factor humano, auditoría de madurez (*DASA Competence Scan*), *AI Coaching* (pasar de *"escribir código"* a *"diseñar el arnés"*) y **Plataforma ValueOps / Dashboard AXIA**.
2. **Servicio Especial 2: Agentic AI-Driven SDLC (DevOps & DevSecOps)**:
   - **Internal Developer Platform (IDP)** sobre **Backstage.io / Roadie** con *Golden Paths* (plantillas YAML) y *Docs-as-Code*.
   - Seguridad *Shift-Left* con **Laguun vCISO** (cumplimiento continuo ENS, DORA, NIS2) y **Xygeni AI Security** (SAST/DAST/SCA + protección OWASP Top 10 for LLM & MCP).
3. **Servicio Especial 3: Agentic AI-Driven QAOps**:
   - Validación continua TDD/BDD e inmunidad del sistema sin UAT manual repetitivo.
   - **Selenium MCP Server** con *Self-Healing* + **JMeter asistido por IA** + **Accelario Test Data Management (TDM)** para datos sintéticos y enmascarados.

---

### Slide 5 · [02] Núcleo Técnico: Plataforma como Producto (5 Capas Agénticas)
| Capa | Disciplina | Implementación en el Proyecto SCA QAOps |
| :--- | :--- | :--- |
| **1. Metodología de Construcción** | **SDD (Spec-Driven Dev)** | Especificación formal en `specs/sdd-segurcaixa-servicios-clientes.md` + Tríada Agéntica (Planificador, Implementador, Revisor) y trazabilidad `@pytest.mark.xray`. |
| **2. Interacción con LLM** | **Prompt Engineering** | Prompts estructurados bajo el patrón **R-C-I-O-V** (*Role, Context, Invariants, Output, Verification*) para POM, Self-Healing y SRE JMeter. |
| **3. Sistema Operativo Agéntico** | **Context Engineering** | Protocolo **MCP** + **DOM Pruning (`-92%` tokens)** en `selenium_inspect_dom_locators` + Carga jerárquica en 4 capas + Memoria compartida ALM. |
| **4. Control y Gobernanza** | **Artefactos Normativos** | Reglas arquitectónicas y límites operativos en `AGENTS.md` y `AGENT.md`. |
| **5. Entrega y Operación** | **Harness & Loop Engineering** | Orquestador `run_qaops_suite.py` que ejecuta el bucle cerrado completo en `< 10 s` y convierte cada fallo en regla automatizada. |

---

### Slide 6 · [03] Demostrador Ejecutable: Portal SegurCaixa Adeslas (`/servicios-para-clientes`)
- **5 Módulos Transaccionales Simulados (`portal-adeslas/app.py`)**:
  1. **Cuadro Médico y Urgencias 24h (`SCA-EP-01`)**: Búsqueda multicriterio por provincia, especialidad y póliza (`Plena Plus`, `Seniors`, `Muface/Isfas`).
  2. **Autorizaciones Médicas Online (`SCA-EP-02`)**: Validación de tarjeta Adeslas (`12-16` dígitos), código `AUT-2026-XXXXX` y derivación a inspección en `Estudio Genético Oncológico`.
  3. **Reembolso de Facturas (`SCA-EP-03`)**: Motor de cobertura (**90%** Adeslas Premier, **80%** Adeslas Extra) y validación IBAN (`^ES\d{22}$`).
  4. **Área Cliente y Tarjeta Sanitaria Digital (`SCA-EP-04`)**.
  5. **Videoconsulta y Orientación Médica 24h (`SCA-EP-04`)**.

---

### Slide 7 · [03] Hub ALM Unificado: Jira + Xray, TestLink y Redmine
- **Dashboard en vivo (`/alm-dashboard`)** e interoperabilidad total:
  - **Jira + Xray (`backlog_xray_export.json`)**: 5 Épicas (`SCA-EP-01..05`), 6 Historias (`SCA-US-101..106`), Plan `SCA-TP-2026-Q4`, 12 Test Cases BDD/Gherkin (`SCA-TC-001..012`) y 2 Defectos (`SCA-BUG-201..202`).
  - **TestLink / TestPlan (`segurcaixa_testplan_testlink.xml`)**: 5 Suites jerárquicas (`TL-SCA-101..112`).
  - **Redmine (`redmine_issues_backlog.csv`)**: Peticiones QA (`#4011..#4022`) y Bugs (`#4091..#4092`).

---

### Slide 8 · [03] Resultados Reales de Certificación: Selenium MCP + JMeter IA (`12/12 PASSED`)
- **Selenium E2E + Servidor MCP (`10/10 PASSED en 5.48s`)**:
  - 7 herramientas MCP (`selenium_start_session`, `selenium_inspect_dom_locators`, `selenium_execute_adeslas_flow`, `alm_sync_test_result`, etc.).
  - Page Object con auto-curación (`find_healed()`) y evidencia automática en `mcp_selftest_servicios_clientes.png`.
- **JMeter 5.6 Asistido por IA (`SLA PASSED`)**:
  - Plan `.jmx` con 3 Thread Groups + motor `ai_jmeter_assistant.py`.
  - **P95 = `72.27 ms`** (frente al umbral máximo de `450 ms`), **Apdex = `1.00`**, **Error Rate = `0.0%`**.
  - Diagnóstico cognitivo que detecta la latencia adicional en `Estudio Genético Oncológico` y recomienda caché Redis vinculada a `SCA-BUG-201`.

---

### Slide 9 · [04] Hoja de Ruta (PoC 8 Semanas / OCM 24 Semanas) e Impacto Medible
- **Plan de PoC (8 Semanas)**:
  - **S1**: Confirmación de casos de uso | **S1-3**: Setup ValueOps, Backstage y MCP | **S2-6**: Desarrollo Tradicional vs. Optimizado | **S7**: Análisis | **S8**: Conclusiones a Dirección.
- **Implantación OCM (24 Semanas)**:
  - **Fase 1 (S1-4)**: Diagnóstico y baseline SLAs | **Fase 2 (S5-8)**: Dashboard AXIA (S6) y primer CMR (S8) | **Fase 3 (S9-20)**: Rollout por oleadas y Comité Multiproveedor | **Fase 4 (S21-24)**: ROI Fase 1 y transferencia.
- **Compromiso de Resultados Cuantificables**:
  - **20-40%** Reducción Time-to-Market | **95%** Automatización QA y ahorro de recirculación | **18% → <2%** Reducción de retrabajos | **35%** Optimización TCO | **100%** Cumplimiento DORA, ENS y AI Act.
