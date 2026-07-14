# Matriz de trazabilidad contra la rúbrica

| Indicador | Evidencia implementada | Archivos principales |
|---|---|---|
| Pipeline ETL robusto (IEE 3.1.1) | Tres fuentes, validación de esquema, logs, caché, reintentos, carga SQL local, lectura por chunks y exportaciones procesadas | `etl/`, `data/`, `logs/` |
| Pandas avanzado (IEE 1.1.1 / IEE 1.2.1) | Groupby multi-clave con múltiples agregaciones, `pivot_table`, lectura por chunks | `etl/transform.py`, `etl/extract.py` |
| Limpieza justificada (IEE 1.3.1) | Conservación de categorías `unknown` + capado IQR de outliers en `balance`/`duration`, ambas cuantificadas y documentadas | `etl/transform.py`, `docs/decisiones_tecnicas.md` |
| Modelos ML supervisados (IEE 2.1.1 / IEP 2.1.3 / IEP 2.2.2) | Clasificación binaria (LogisticRegression + RandomForest) sobre `conversion_flag`, con `GridSearchCV`, métricas e interpretabilidad | `models/`, `docs/decisiones_tecnicas.md` |
| Documentación completa | Arquitectura, API, manual de usuario, decisiones técnicas y diagrama Mermaid | `README.md`, `docs/` |
| Dashboard interactivo (IEP 3.1.1) | Vistas ejecutiva, operativa y técnica con Plotly, filtros, comparación de modelos y terminología por audiencia | `dashboards/` |
| Git profesional | Estrategia de ramas, issues planificados y checklist de evidencias para completar al final | `docs/colaboracion/` |
| Ejecución reproducible local | Entorno virtual, `.env`, scripts de ejecución, SQLite local y guía paso a paso | `.env.example`, `scripts/`, `README.md` |
| Presentación | Guion de 15 minutos, demo local y distribución de responsabilidades | `docs/presentacion.md` |

## Nota sobre Docker

Docker fue considerado inicialmente, pero el equipo decidió no utilizarlo porque la evaluación se defenderá mediante ejecución local reproducible. La solución mantiene configuración externa mediante `.env`, scripts de ejecución y documentación paso a paso. No es uno de los indicadores puntuados (IEE/IEP) de la pauta; es un riesgo de forma frente al enunciado del Encargo, asumido conscientemente.

## Elementos pendientes de ejecución real por el equipo

- Crear repositorio remoto.
- Abrir issues reales.
- Crear ramas reales.
- Realizar pull requests y revisiones cruzadas.
- Capturar evidencias de GitHub.
- Ejecutar el proyecto completo en el equipo de presentación.
- Ejecutar `pytest` y guardar evidencia del resultado.
