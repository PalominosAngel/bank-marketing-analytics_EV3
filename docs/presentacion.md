# Estructura sugerida para presentación individual — 15 minutos

## 1. Problema y objetivo — 1 minuto

Explicar que el proyecto transforma datos de campañas bancarias en información útil para gerencia, analistas y personal operativo.

## 2. Arquitectura end-to-end — 2 minutos

Mostrar el diagrama y explicar las tres fuentes: CSV, API REST externa y tabla SQL local de referencia. Indicar que el pipeline valida, transforma, segmenta y persiste resultados en SQLite.

## 3. Demo del ETL — 3 minutos

Ejecutar:

```bash
python -m etl.pipeline
```

Mostrar logs, estado exitoso, filas procesadas, archivos generados y registro en `etl_runs`. Mencionar que la API externa posee reintentos y respaldo de caché.

## 4. API propia — 2 minutos

Abrir `http://localhost:8000/docs` y ejecutar:

- `/health`
- `/api/kpis`
- `/api/etl-runs`
- `/api/segments`

Explicar que FastAPI separa la capa de datos de la visualización y permite consultar resultados procesados de forma ordenada.

## 5. Dashboard por audiencia — 4 minutos

- Ejecutiva: KPIs, conversión y decisiones comerciales.
- Operativa: filtros, canales de contacto y descarga de clientes filtrados.
- Técnica: calidad de datos, trazabilidad del ETL, PCA, K-Means y correlaciones.

## 6. Git y colaboración — 1 minuto

Mostrar ramas, commits, issues, pull requests y revisiones cruzadas cuando el repositorio esté preparado.

## 7. Decisiones técnicas — 1 minuto

Explicar que el equipo decidió ejecutar localmente con Python, `.env` y SQLite para facilitar la instalación, reducir fricción técnica y asegurar una demo estable.

## 8. Lecciones aprendidas y mejoras — 2 minutos

Comentar separación por capas, importancia del manejo de errores, utilidad del caché y futuras mejoras: autenticación, programación automática del ETL, monitoreo, despliegue cloud y pruebas de carga.
