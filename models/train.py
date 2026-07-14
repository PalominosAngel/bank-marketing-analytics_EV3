"""Orquestador de entrenamiento: python -m models.train"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

import joblib
import pandas as pd

from etl.logging_config import configure_logging
from models.classification import EXCLUDED_LEAKAGE_FEATURES, FEATURE_COLUMNS, TARGET_COLUMN, train_and_evaluate

PROCESSED_CSV = Path("data/processed/customers_processed.csv")
ARTIFACTS_DIR = Path("models/artifacts")
METRICS_PATH = Path("models/metrics.json")


def _load_processed_customers() -> pd.DataFrame:
    if not PROCESSED_CSV.exists():
        raise FileNotFoundError(f"No existe {PROCESSED_CSV}. Ejecuta primero: python -m etl.pipeline")
    return pd.read_csv(PROCESSED_CSV)


def run_training() -> dict:
    logger = configure_logging(log_file="logs/models.log")
    logger.info("Cargando datos procesados desde %s", PROCESSED_CSV)
    df = _load_processed_customers()

    results = train_and_evaluate(df)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, result in results.items():
        joblib.dump(result.pipeline, ARTIFACTS_DIR / f"{name}.joblib")
        logger.info(
            "%s entrenado — ROC AUC test: %.4f (CV: %.4f)",
            name, result.test_roc_auc, result.cv_best_roc_auc,
        )

    best_name = max(results, key=lambda name: results[name].test_roc_auc)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": TARGET_COLUMN,
        "feature_columns": FEATURE_COLUMNS,
        "excluded_leakage_features": EXCLUDED_LEAKAGE_FEATURES,
        "best_model": best_name,
        "models": {
            name: {
                "best_params": result.best_params,
                "cv_best_roc_auc": result.cv_best_roc_auc,
                "test_roc_auc": result.test_roc_auc,
                "test_accuracy": result.test_accuracy,
                "classification_report": result.classification_report,
                "confusion_matrix": result.confusion_matrix,
                "interpretability": result.interpretability,
            }
            for name, result in results.items()
        },
    }
    METRICS_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Mejor modelo: %s — métricas guardadas en %s", best_name, METRICS_PATH)
    print(f"Entrenamiento completado. Mejor modelo: {best_name} (ROC AUC test: {results[best_name].test_roc_auc})")
    return summary


if __name__ == "__main__":
    run_training()
