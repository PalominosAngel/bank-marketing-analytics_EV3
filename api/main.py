"""API REST propia para exponer resultados del pipeline."""
from __future__ import annotations

from pathlib import Path
import json

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from api.database import db
from api.schemas import HealthResponse

MODEL_METRICS_PATH = Path("models/metrics.json")

app = FastAPI(
    title="Bank Marketing Analytics API",
    description="API de consulta para resultados procesados del pipeline ETL.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


def records(frame: pd.DataFrame) -> list[dict]:
    return frame.where(pd.notnull(frame), None).to_dict(orient="records")


def safe_query(query: str, params: dict | None = None) -> pd.DataFrame:
    try:
        return db.read_sql(query, params=params)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datos no disponibles. Ejecuta primero el ETL. Detalle: {exc}") from exc


@app.get("/health", response_model=HealthResponse)
def health() -> dict:
    return {"status": "ok", "service": "bank-marketing-analytics-api"}


@app.get("/api/kpis")
def get_kpis() -> dict:
    frame = safe_query("""
        SELECT
            COUNT(*) AS total_customers,
            ROUND(AVG(conversion_flag) * 100, 2) AS conversion_rate_pct,
            ROUND(AVG(balance), 2) AS average_balance,
            ROUND(AVG(duration_minutes), 2) AS average_duration_minutes,
            SUM(CASE WHEN conversion_flag = 1 THEN 1 ELSE 0 END) AS conversions
        FROM customers_processed
    """)
    return records(frame)[0]


@app.get("/api/customers")
def get_customers(
    limit: int = Query(500, ge=1, le=5000),
    job: str | None = None,
    segment: int | None = None,
    converted: int | None = Query(None, ge=0, le=1),
) -> list[dict]:
    conditions = []
    params: dict = {"limit": limit}
    if job:
        conditions.append("job = :job")
        params["job"] = job
    if segment is not None:
        conditions.append("customer_segment = :segment")
        params["segment"] = segment
    if converted is not None:
        conditions.append("conversion_flag = :converted")
        params["converted"] = converted
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    frame = safe_query(f"SELECT * FROM customers_processed {where} LIMIT :limit", params)
    return records(frame)


@app.get("/api/segments")
def get_segments() -> list[dict]:
    return records(safe_query("SELECT * FROM segment_summary ORDER BY customer_segment"))


@app.get("/api/economic-indicators")
def get_economic_indicators() -> list[dict]:
    return records(safe_query("SELECT * FROM macroeconomic_indicators ORDER BY year, indicator_code"))


@app.get("/api/data-quality")
def get_data_quality() -> list[dict]:
    return records(safe_query("SELECT * FROM data_quality_report ORDER BY metric"))


@app.get("/api/etl-runs")
def get_etl_runs() -> list[dict]:
    return records(safe_query("SELECT * FROM etl_runs ORDER BY started_at DESC LIMIT 20"))


@app.get("/api/profile/job-marital")
def get_job_marital_profile() -> list[dict]:
    return records(safe_query("SELECT * FROM job_marital_profile ORDER BY job, marital"))


@app.get("/api/conversion-pivot")
def get_conversion_pivot() -> list[dict]:
    return records(safe_query("SELECT * FROM conversion_pivot_by_month_channel"))


@app.get("/models/metrics")
def get_model_metrics() -> dict:
    if not MODEL_METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Aún no se entrenaron modelos. Ejecuta primero: python -m models.train",
        )
    return json.loads(MODEL_METRICS_PATH.read_text(encoding="utf-8"))
