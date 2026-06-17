"""Orquestador del pipeline end-to-end."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import uuid

from etl.config import settings
from etl.database import DatabaseManager
from etl.extract import extract_bank_csv, extract_channel_reference, extract_world_bank_indicators
from etl.load import load_all
from etl.logging_config import configure_logging
from etl.transform import transform_customers, build_segment_summary
from etl.validators import validate_bank_schema, metrics_to_frame


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_pipeline() -> dict:
    logger = configure_logging(settings.log_level)
    run_id = f"etl-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    db = DatabaseManager(settings.database_url)
    db.initialize_schema()

    record = {
        "run_id": run_id,
        "started_at": utc_now(),
        "finished_at": None,
        "status": "running",
        "rows_extracted": 0,
        "rows_loaded": 0,
        "api_source_status": None,
        "error_message": None,
    }
    db.upsert_etl_run(record)

    try:
        logger.info("Iniciando pipeline %s", run_id)
        raw_customers = extract_bank_csv(settings.bank_csv_path)
        record["rows_extracted"] = len(raw_customers)
        logger.info("Fuente CSV extraída: %s filas", len(raw_customers))

        channel_reference = extract_channel_reference(db)
        logger.info("Fuente SQL extraída: %s canales de contacto", len(channel_reference))

        api_result = extract_world_bank_indicators(settings)
        record["api_source_status"] = api_result.source_status
        logger.info("Fuente API externa extraída con estado: %s", api_result.source_status)

        metrics = validate_bank_schema(raw_customers)
        quality_report = metrics_to_frame(metrics, run_id)
        customers = transform_customers(
            raw_customers,
            channel_reference,
            Path("data/processed/clustering_metadata.json"),
        )
        segment_summary = build_segment_summary(customers)
        load_all(
            db,
            customers,
            api_result.data,
            quality_report,
            segment_summary,
            Path("data/processed"),
        )

        record.update({
            "finished_at": utc_now(),
            "status": "success",
            "rows_loaded": len(customers),
        })
        db.upsert_etl_run(record)
        logger.info("Pipeline completado: %s filas cargadas", len(customers))
        return record
    except Exception as exc:
        record.update({"finished_at": utc_now(), "status": "error", "error_message": str(exc)})
        db.upsert_etl_run(record)
        logger.exception("Pipeline finalizado con error")
        raise


if __name__ == "__main__":
    run_pipeline()
