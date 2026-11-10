# Informe de Rendimiento JMeter Asistido por IA — SegurCaixa Adeslas

- **Fecha de Ejecución**: `2026-11-10 21:17:14 UTC`
- **Escenario**: Campaña Salud SegurCaixa Adeslas - Ejecución JMeter AI
- **Estado del Quality Gate (SLA P95 < 450ms)**: **PASSED**

## 1. Métricas Globales de Rendimiento

| Métrica | Valor Obtenido | Umbral SLA SegurCaixa Adeslas |
| :--- | :--- | :--- |
| Muestras Totales | `60` | >= 50 |
| Throughput | `120.0 req/s` | >= 15 req/s |
| Tiempo Medio (Avg) | `22.89 ms` | < 200 ms |
| Percentil 90 (P90) | `66.49 ms` | < 350 ms |
| Percentil 95 (P95) | `72.27 ms` | **< 450 ms** |
| Percentil 99 (P99) | `83.75 ms` | < 800 ms |
| Tasa de Error | `0.0%` | <= 1.0% |
| Índice Apdex | `1.0` | >= 0.90 |

## 2. Desglose por Transacción / Endpoint

| Endpoint / Transacción | Muestras | Media (ms) | P95 (ms) | Error % |
| :--- | :--- | :--- | :--- | :--- |
| `GET /api/v1/cuadro-medico` | 24 | 10.74 ms | **21.37 ms** | 0.0% |
| `POST /api/v1/reembolsos` | 12 | 10.44 ms | **23.31 ms** | 0.0% |
| `POST /api/v1/autorizaciones` | 12 | 11.51 ms | **22.27 ms** | 0.0% |
| `POST /api/v1/autorizaciones (Estudio Genético)` | 12 | 71.0 ms | **83.75 ms** | 0.0% |

## 3. Diagnóstico Cognitivo del Agente JMeter IA (Ayesa Digital)

- Cumplimiento SLA Global: APROBADO (P95 = 72.27 ms frente al objetivo < 450.0 ms; Error Rate = 0.0%).
- Índice de satisfacción de usuario Apdex = 1.0 con un caudal sostenido de 120.0 req/s (60 transacciones).
- Detección de Anomalía IA en 'POST /api/v1/autorizaciones (Estudio Genético)': P95 = 83.75 ms (superior a la media general de 22.89 ms). Causa raíz identificada: validación síncrona de baremos de inspección médica. Acción recomendada vinculada al defecto SCA-BUG-201: activar caché Redis para reglas de baremo.
