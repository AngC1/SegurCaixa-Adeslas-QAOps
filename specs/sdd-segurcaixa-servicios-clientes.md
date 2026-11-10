# Especificación SDD (Spec-Driven Development) — SegurCaixa Adeslas (`/servicios-para-clientes`)

- **ID de Especificación**: `SDD-SCA-2026-001`
- **Estado**: `APPROVED & VERIFIED (12/12 Tests Passing)`
- **Propietario**: Unidad de Ingeniería QAOps — Ayesa Digital

---

## 1. Contratos de Dominio y API REST

### 1.1 Buscador de Cuadro Médico (`GET /api/v1/cuadro-medico`)
- **Parámetros Query**:
  - `provincia` (`string`, opcional): `Madrid | Barcelona | Sevilla | Valencia | Bilbao | Todas`
  - `especialidad` (`string`, opcional): `Cardiología | Dermatología | Pediatría | Traumatología | Urgencias 24h | Dental | Todas`
  - `poliza` (`string`, opcional): `Adeslas Plena Plus | Adeslas Plena Vital | Adeslas Seniors | Adeslas Premier | Muface / Isfas | Todas`
  - `q` (`string`, opcional): Búsqueda textual insensible a mayúsculas sobre nombre del centro, facultativo o dirección.
- **Invariante de Respuesta (`HTTP 200`)**:
  - Devuelve `{"filtros": {...}, "total": <int>, "resultados": [...]}`.
- **Trazabilidad QA**: `SCA-TC-002` (`TL-SCA-102`), `SCA-TC-003` (`TL-SCA-103`), `SCA-TC-011` (`TL-SCA-111`).

### 1.2 Tramitación de Autorizaciones Médicas (`POST /api/v1/autorizaciones`)
- **Payload JSON de Entrada**:
  - `numTarjeta`: Cadena numérica de 12 a 16 dígitos (`^\d{12,16}$`).
  - `tipoActo`: Tipo de prueba diagnóstica o acto médico.
  - `codigoPrescripcion`: Identificador del volante médico.
  - `centroMedico`: Nombre del hospital o centro concertado.
- **Reglas de Negocio Verificables**:
  - **RN-AUT-01**: Si `numTarjeta` no cumple `^\d{12,16}$`, retorna `HTTP 400` con `errorCode: "INVALID_CARD_NUMBER"`.
  - **RN-AUT-02**: Si `tipoActo` contiene `genético` u `oncol`, retorna `HTTP 201` con `estado: "PENDIENTE_REVISION_MEDICA"`.
  - **RN-AUT-03**: En cualquier otro acto válido, retorna `HTTP 201` con `estado: "AUTORIZADA"` y código `AUT-2026-XXXXX`.
- **Trazabilidad QA**: `SCA-TC-004` (`TL-SCA-104`), `SCA-TC-005` (`TL-SCA-105`), `SCA-TC-006` (`TL-SCA-106`), `SCA-TC-012` (`TL-SCA-112`).

### 1.3 Gestión de Reembolsos (`POST /api/v1/reembolsos`)
- **Payload JSON de Entrada**:
  - `nif`: Formato `^[0-9XYZ]\d{7}[A-Z]$`.
  - `modalidadPoliza`: `Adeslas Premier (90%)` o `Adeslas Extra (80%)`.
  - `importeFactura`: Número real `> 0`.
  - `iban`: Formato español `^ES\d{22}$`.
- **Reglas de Negocio Verificables**:
  - **RN-RMB-01**: Cobertura del `90%` para modalidad `Premier` y `80%` para `Extra` (`importeEstimadoReembolso = round(importeFactura * cobertura, 2)`).
  - **RN-RMB-02**: Si el IBAN no cumple `^ES\d{22}$`, retorna `HTTP 400` con `errorCode: "INVALID_IBAN"`.
- **Trazabilidad QA**: `SCA-TC-007` (`TL-SCA-107`), `SCA-TC-008` (`TL-SCA-108`).

### 1.4 Área Cliente y Salud Digital (`POST /api/v1/auth/login` y `POST /api/v1/citas`)
- **Reglas de Negocio Verificables**:
  - **RN-CLI-01**: Login válido con `12345678Z` / `Adeslas2026!` despliega póliza `POL-SCA-908122` y Tarjeta Digital `8000123456789012`.
  - **RN-CIT-01**: Solicitud de videoconsulta con motivo válido retorna `HTTP 201`, estado `CONFIRMADA` y código `CIT-2026-XXXXX`.
- **Trazabilidad QA**: `SCA-TC-009` (`TL-SCA-109`), `SCA-TC-010` (`TL-SCA-110`).
