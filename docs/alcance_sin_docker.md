# Alcance de ejecución sin Docker

El equipo decidió no utilizar Docker en esta versión del proyecto. La ejecución se realiza localmente mediante:

1. Entorno virtual de Python.
2. Archivo `.env` para configuración externa.
3. SQLite como base de datos local.
4. Scripts de apoyo en `scripts/`.
5. Documentación paso a paso en la sección de instalación del `README.md`.

## Justificación

La prioridad del equipo es asegurar una demo estable y defendible, reduciendo dependencias de infraestructura que no fueron necesarias para cumplir el flujo analítico principal: extracción, transformación, validación, carga, API y dashboard.

## Comandos principales

```bash
python -m etl.pipeline
uvicorn api.main:app --reload
streamlit run dashboards/app.py
pytest
```
