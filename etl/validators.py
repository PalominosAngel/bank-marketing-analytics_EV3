"""Validación explícita de esquema y reglas de calidad de datos."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import pandas as pd


REQUIRED_COLUMNS = {
    "age", "job", "marital", "education", "default", "balance", "housing",
    "loan", "contact", "day", "month", "duration", "campaign", "pdays",
    "previous", "poutcome", "y",
}
NUMERIC_COLUMNS = ["age", "balance", "day", "duration", "campaign", "pdays", "previous"]
BINARY_COLUMNS = ["default", "housing", "loan", "y"]


@dataclass
class QualityMetric:
    metric: str
    value: float | int | str
    severity: str
    description: str


def validate_bank_schema(df: pd.DataFrame) -> list[QualityMetric]:
    """Valida columnas, duplicados, nulos y dominios básicos.

    Lanza excepciones solo cuando el pipeline no puede continuar. Los problemas
    informativos quedan registrados como métricas para el dashboard técnico.
    """
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Faltan columnas obligatorias en bank.csv: {missing}")

    metrics: list[QualityMetric] = []
    metrics.append(QualityMetric("rows_received", len(df), "info", "Cantidad de registros extraídos desde CSV"))
    metrics.append(QualityMetric("duplicate_rows", int(df.duplicated().sum()), "warning", "Filas duplicadas exactas detectadas"))
    metrics.append(QualityMetric("null_cells", int(df.isna().sum().sum()), "warning", "Celdas nulas detectadas"))

    for column in NUMERIC_COLUMNS:
        converted = pd.to_numeric(df[column], errors="coerce")
        invalid = int(converted.isna().sum() - df[column].isna().sum())
        if invalid > 0:
            raise ValueError(f"La columna numérica '{column}' contiene {invalid} valores inválidos")

    for column in BINARY_COLUMNS:
        invalid_values = sorted(set(df[column].dropna().astype(str).str.lower()) - {"yes", "no"})
        if invalid_values:
            raise ValueError(f"La columna binaria '{column}' contiene valores no permitidos: {invalid_values}")

    categorical_columns = df.select_dtypes(include="object").columns
    unknown_count = int((df[categorical_columns] == "unknown").sum().sum())
    metrics.append(QualityMetric("unknown_category_cells", unknown_count, "info", "Categorías 'unknown' conservadas para trazabilidad"))

    age_outliers = int(((pd.to_numeric(df["age"]) < 18) | (pd.to_numeric(df["age"]) > 100)).sum())
    metrics.append(QualityMetric("age_outliers", age_outliers, "warning", "Edades fuera del rango esperado 18-100"))
    return metrics


def metrics_to_frame(metrics: list[QualityMetric], run_id: str) -> pd.DataFrame:
    frame = pd.DataFrame([asdict(metric) for metric in metrics])
    frame.insert(0, "run_id", run_id)
    return frame
