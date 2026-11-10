# Informe de Rendimiento JMeter Asistido por IA — SegurCaixa Adeslas

- **Fecha de Ejecución**: `2026-11-10 20:13:30 UTC`
- **Escenario**: Campaña Salud SegurCaixa Adeslas - Ejecución JMeter AI
- **Estado del Quality Gate (SLA P95 < 450ms)**: **PASSED**

## 1. Métricas Globales de Rendimiento

| Métrica | Valor Obtenido | Umbral SLA SegurCaixa Adeslas |
| :--- | :--- | :--- |
| Muestras Totales | `60` | >= 50 |
| Throughput | `120.0 req/s` | >= 15 req/s |
| Tiempo Medio (Avg) | `21.19 ms` | < 200 ms |
| Percentil 90 (P90) | `67.12 ms` | < 350 ms |
| Percentil 95 (P95) | `70.13 ms` | **< 450 ms** |
| Percentil 99 (P99) | `79.98 ms` | < 800 ms |
| Tasa de Error | `0.0%` | <= 1.0% |
| Índice Apdex | `1.0` | >= 0.90 |

## 2. Desglose por Transacción / Endpoint

| Endpoint / Transacción | Muestras | Media (ms) | P95 (ms) | Error % |
| :--- | :--- | :--- | :--- | :--- |
| `GET /api/v1/cuadro-medico` | 24 | 9.13 ms | **20.93 ms** | 0.0% |
| `POST /api/v1/autorizaciones` | 12 | 8.92 ms | **19.04 ms** | 0.0% |
| `POST /api/v1/autorizaciones (Estudio Genético)` | 12 | 68.92 ms | **80.1 ms** | 0.0% |
| `POST /api/v1/reembolsos` | 12 | 9.85 ms | **21.42 ms** | 0.0% |

## 3. Diagnóstico Cognitivo del Agente JMeter IA (Ayesa Digital)

- Cumplimiento SLA Global: APROBADO (P95 = 70.13 ms frente al objetivo < 450.0 ms; Error Rate = 0.0%).
- Índice de satisfacción de usuario Apdex = 1.0 con un caudal sostenido de 120.0 req/s (60 transacciones).
- Detección de Anomalía IA en 'POST /api/v1/autorizaciones (Estudio Genético)': P95 = 80.1 ms (superior a la media general de 21.19 ms). Causa raíz identificada: validación síncrona de baremos de inspección médica. Acción recomendada vinculada al defecto SCA-BUG-201: activar caché Redis para reglas de baremo.
