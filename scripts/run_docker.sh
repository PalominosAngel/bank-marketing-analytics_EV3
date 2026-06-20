#!/usr/bin/env bash
# Despliegue del proyecto completo con Docker Compose.
# Uso: ./scripts/run_docker.sh [up|down|logs|rebuild]
set -euo pipefail

cd "$(dirname "$0")/.."

ACTION="${1:-up}"

case "$ACTION" in
  up)
    echo "==> Construyendo imagenes y levantando el stack..."
    docker compose up --build -d
    echo ""
    echo "ETL ejecutado, API y dashboard arrancando."
    echo "  API:       http://localhost:${API_PORT:-8000}/docs"
    echo "  Dashboard: http://localhost:${DASHBOARD_PORT:-8501}"
    echo ""
    echo "Ver estado:  docker compose ps"
    echo "Ver logs:    ./scripts/run_docker.sh logs"
    ;;
  down)
    echo "==> Deteniendo el stack (los datos persisten en el volumen app-data)..."
    docker compose down
    ;;
  logs)
    docker compose logs -f
    ;;
  rebuild)
    echo "==> Reconstruyendo desde cero (sin cache)..."
    docker compose build --no-cache
    docker compose up -d
    ;;
  *)
    echo "Accion no reconocida: $ACTION"
    echo "Uso: $0 [up|down|logs|rebuild]"
    exit 1
    ;;
esac
