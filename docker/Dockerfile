# Imagen comun para ETL, API y dashboard.
# Multi-stage para mantener la imagen final liviana (sin cache de pip ni toolchain de build).

# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Entorno virtual aislado que luego se copia al runtime.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Capa de dependencias separada del codigo para aprovechar el cache de Docker.
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Usuario no-root por seguridad.
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# Solo el entorno virtual con las dependencias ya instaladas.
COPY --from=builder /opt/venv /opt/venv

# Codigo de la aplicacion.
COPY . .

# Directorio de la base SQLite generada por el ETL (punto de montaje del volumen).
# Se crea con ownership de appuser para que el named volume herede permisos de escritura.
RUN mkdir -p /app/data/database && chown -R appuser:appuser /app

USER appuser

# Comando por defecto: API. Cada servicio del compose lo sobrescribe con su propio command.
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
