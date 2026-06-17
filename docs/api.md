# Documentación de API

La API propia se levanta en `http://localhost:8000`. FastAPI genera documentación interactiva en `http://localhost:8000/docs`.

| Método | Endpoint | Propósito |
|---|---|---|
| GET | `/health` | Verificar disponibilidad del servicio. |
| GET | `/api/kpis` | Consultar indicadores ejecutivos agregados. |
| GET | `/api/customers` | Consultar clientes procesados con filtros opcionales. |
| GET | `/api/segments` | Consultar el resumen de segmentos K-Means. |
| GET | `/api/economic-indicators` | Consultar datos obtenidos desde la API externa. |
| GET | `/api/data-quality` | Consultar métricas de calidad del último pipeline. |
| GET | `/api/etl-runs` | Revisar historial de ejecuciones ETL. |

## Ejemplos

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/kpis
curl "http://localhost:8000/api/customers?job=management&converted=1&limit=100"
```
