#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
cp -n .env.example .env || true
python -m etl.pipeline

echo "ETL completado. Ejecuta en dos terminales adicionales:"
echo "  source .venv/bin/activate && uvicorn api.main:app --reload"
echo "  source .venv/bin/activate && streamlit run dashboards/app.py"
