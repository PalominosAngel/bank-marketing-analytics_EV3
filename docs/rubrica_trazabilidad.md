# Matriz de trazabilidad contra la rúbrica

| Indicador | Evidencia implementada | Archivos principales |
|---|---|---|
| Pipeline ETL robusto | Tres fuentes, validación de esquema, logs, caché, reintentos, carga SQL local y exportaciones procesadas | `etl/`, `data/`, `logs/` |
| Documentación completa | Arquitectura, API, manual de usuario, guía de ejecución local, decisiones técnicas y diagrama Mermaid | `README.md`, `docs/` |
| Dashboard interactivo | Vistas ejecutiva, operativa y técnica con Plotly, filtros y terminología por audiencia | `dashboards/` |
| Git profesional | Estrategia de ramas, issues planificados y checklist de evidencias para completar al final | `repo/` |
| Ejecución reproducible local | Entorno virtual, `.env`, scripts de ejecución, SQLite local y guía paso a paso | `.env.example`, `scripts/`, `docs/guia_despliegue.md` |
| Presentación | Guion de 15 minutos, demo local y distribución de responsabilidades | `docs/presentacion.md` |

## Nota sobre Docker

Docker fue considerado inicialmente, pero el equipo decidió no utilizarlo porque la evaluación se defenderá mediante ejecución local reproducible. La solución mantiene configuración externa mediante `.env`, scripts de ejecución y documentación paso a paso.

## Elementos pendientes de ejecución real por el equipo

- Crear repositorio remoto.
- Abrir issues reales.
- Crear ramas reales.
- Realizar pull requests y revisiones cruzadas.
- Capturar evidencias de GitHub.
- Ejecutar el proyecto completo en el equipo de presentación.
- Ejecutar `pytest` y guardar evidencia del resultado.
