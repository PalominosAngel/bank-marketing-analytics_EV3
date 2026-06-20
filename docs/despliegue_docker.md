# Guía de despliegue con Docker

Esta guía describe cómo construir y ejecutar el proyecto completo (ETL + API + dashboard) en contenedores, sin instalar dependencias de Python en la máquina anfitriona.

## Arquitectura de contenedores

El proyecto usa **una sola imagen** común (definida en `docker/Dockerfile`) reutilizada por tres servicios, porque ETL, API y dashboard comparten el mismo código y dependencias. Esto reduce el tiempo de build y el tamaño total (una build, capas reutilizadas).

| Servicio | Rol | Comando | Puerto |
|---|---|---|---|
| `etl` | Ejecuta el pipeline una vez y genera la base SQLite | `python -m etl.pipeline` | — |
| `api` | Expone los resultados procesados (FastAPI) | `uvicorn api.main:app` | 8000 |
| `dashboard` | Visualiza los datos (Streamlit) | `streamlit run dashboards/app.py` | 8501 |

```
┌──────────┐   genera    ┌─────────────────┐
│   etl    │ ─────────►  │ volumen app-data │ ◄──── lee ──── ┌──────────┐
│  (job)   │   bank.db   │  (SQLite)        │                │   api    │
└──────────┘             └─────────────────┘                └────┬─────┘
                                                                  │ HTTP
                                                            ┌─────▼──────┐
                                                            │ dashboard  │
                                                            └────────────┘
```

### Orden de arranque (orquestación)

Compose respeta las dependencias automáticamente:

1. `etl` corre primero y debe **terminar con éxito** (`service_completed_successfully`).
2. `api` arranca después del ETL y expone un **healthcheck** en `/health`.
3. `dashboard` arranca solo cuando la API está **sana** (`service_healthy`).

Esto evita el error 503 "Ejecuta primero el ETL" que ocurriría si la API arrancara sin datos.

## Optimizaciones aplicadas

- **Multi-stage build**: el `builder` instala dependencias en un venv; el `runtime` solo copia el venv, sin cache de pip ni toolchain.
- **Imagen base `python:3.12-slim`**: liviana y alineada con la versión soportada (evita el fallo de compilación de `psycopg2-binary` en Python 3.14).
- **Usuario no-root** (`appuser`): el contenedor no corre como root.
- **`.dockerignore`**: excluye `.git`, `.venv`, `docs`, notebooks y la base local del contexto de build.
- **Capa de dependencias separada del código**: cambiar el código no invalida la instalación de dependencias.

## Requisitos

- Docker 24+ y Docker Compose v2+ (`docker compose version`).

## Configuración externa (variables de entorno)

Las variables tienen valores por defecto en `docker-compose.yml` y se pueden sobrescribir creando un archivo `.env` en la raíz del proyecto (Compose lo lee automáticamente):

```env
APP_ENV=production
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///data/database/bank_analytics.db
API_BASE_URL=http://api:8000
API_PORT=8000
DASHBOARD_PORT=8501
```

> Para usar PostgreSQL en lugar de SQLite, basta con apuntar `DATABASE_URL` a la instancia correspondiente (la imagen ya incluye `psycopg2-binary`).

## Comandos

Con el script de apoyo:

```bash
./scripts/run_docker.sh up        # build + levantar todo en segundo plano
./scripts/run_docker.sh logs      # seguir los logs
./scripts/run_docker.sh down      # detener (los datos persisten en el volumen)
./scripts/run_docker.sh rebuild   # reconstruir sin cache
```

O directamente con Compose:

```bash
docker compose up --build -d      # construir y levantar
docker compose ps                 # ver estado de los servicios
docker compose logs -f api        # logs de un servicio
docker compose down               # detener
docker compose down -v            # detener y borrar el volumen de datos
```

## Acceso

- **API (Swagger UI):** http://localhost:8000/docs
- **Dashboard:** http://localhost:8501

## Persistencia

La base SQLite generada por el ETL vive en el volumen nombrado `app-data`, montado en `/app/data/database`. Sobrevive a `docker compose down` y se comparte entre los servicios `etl` y `api`. Para empezar de cero: `docker compose down -v`.

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `api` devuelve 503 | El ETL no generó la base | Revisar `docker compose logs etl`; reconstruir con `rebuild` |
| Dashboard no carga datos | `API_BASE_URL` mal configurada | Debe ser `http://api:8000` dentro de la red de Compose |
| Puerto ocupado | 8000/8501 en uso | Override `API_PORT` / `DASHBOARD_PORT` en `.env` |
