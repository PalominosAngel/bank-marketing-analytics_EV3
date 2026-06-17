# Guía de instalación y ejecución local

Esta guía explica cómo ejecutar el proyecto sin Docker, usando un entorno virtual de Python y una base de datos SQLite local.

## 1. Requisitos

- Python 3.12 recomendado.
- Terminal de macOS, Linux o Windows con soporte para Python.
- Conexión a internet para actualizar los indicadores de World Bank API.

## 2. Crear entorno virtual

Desde la carpeta raíz del proyecto:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

En caso de usar Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Crear archivo de configuración

```bash
cp .env.example .env
```

La configuración por defecto utiliza SQLite:

```env
DATABASE_URL=sqlite:///data/database/bank_analytics.db
```

## 5. Ejecutar el pipeline ETL

```bash
python -m etl.pipeline
```

Resultado esperado:

```text
Fuente CSV extraída: 4521 filas
Fuente SQL extraída: 3 canales de contacto
Fuente API externa extraída con estado: live_api
Pipeline completado: 4521 filas cargadas
```

Si no hay conexión a internet, el pipeline utilizará el caché local y registrará el estado `cache_fallback`.

## 6. Levantar la API

Abrir una segunda terminal:

```bash
cd bank-marketing-analytics
source .venv/bin/activate
uvicorn api.main:app --reload
```

Servicios disponibles:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## 7. Levantar el dashboard

Abrir una tercera terminal:

```bash
cd bank-marketing-analytics
source .venv/bin/activate
streamlit run dashboards/app.py
```

Dashboard disponible en:

- `http://localhost:8501`

## 8. Ejecutar pruebas automatizadas

```bash
pytest
```

Resultado esperado:

```text
9 passed
```

## 9. Verificación de contingencia

Para demostrar tolerancia a fallos, se puede ejecutar el pipeline sin conexión a internet. El proceso utilizará `data/cache/world_bank_indicators_cache.json` y registrará `cache_fallback` en `etl_runs`.

## 10. Comandos rápidos

```bash
bash scripts/run_local.sh
```

```bash
bash scripts/run_tests.sh
```
