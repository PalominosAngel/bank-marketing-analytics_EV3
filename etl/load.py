"""Carga transaccional de resultados procesados."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from etl.database import DatabaseManager


def load_all(
    db: DatabaseManager,
    customers: pd.DataFrame,
    macroeconomic: pd.DataFrame,
    quality_report: pd.DataFrame,
    segment_summary: pd.DataFrame,
    processed_dir: Path,
) -> None:
    """Persiste tablas y exporta CSV procesados para auditoría."""
    processed_dir.mkdir(parents=True, exist_ok=True)
    db.replace_table(customers, "customers_processed")
    db.replace_table(macroeconomic, "macroeconomic_indicators")
    db.replace_table(quality_report, "data_quality_report")
    db.replace_table(segment_summary, "segment_summary")

    customers.to_csv(processed_dir / "customers_processed.csv", index=False)
    macroeconomic.to_csv(processed_dir / "macroeconomic_indicators.csv", index=False)
    quality_report.to_csv(processed_dir / "data_quality_report.csv", index=False)
    segment_summary.to_csv(processed_dir / "segment_summary.csv", index=False)
