"""Transformaciones de negocio reproducibles."""
from __future__ import annotations

import pandas as pd

from etl.clustering import add_customer_segments
from etl.validators import QualityMetric


MONTH_ORDER = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

OUTLIER_COLUMNS = ["balance", "duration"]


def cap_outliers_iqr(df: pd.DataFrame, columns: list[str], multiplier: float = 1.5) -> tuple[pd.DataFrame, list[QualityMetric]]:
    """Capa (winsoriza) outliers vía rango intercuartílico en lugar de eliminarlos.

    Segunda técnica de limpieza, distinta de "conservar categorías unknown": aquí el
    valor extremo sí se ajusta, porque una fila con `balance` o `duration` fuera de
    escala distorsiona por igual a K-Means/PCA (etl/clustering.py) y a los modelos
    supervisados (models/classification.py) sin aportar señal adicional más allá de
    "es un extremo". Se capa en vez de eliminar para no perder registros en un
    dataset de solo 4521 filas.
    """
    result = df.copy()
    metrics: list[QualityMetric] = []
    for column in columns:
        q1, q3 = result[column].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
        affected = int(((result[column] < lower) | (result[column] > upper)).sum())
        result[column] = result[column].clip(lower=lower, upper=upper)
        metrics.append(QualityMetric(
            metric=f"{column}_outliers_capped",
            value=affected,
            severity="info",
            description=f"Valores de '{column}' capados a [{lower:.1f}, {upper:.1f}] vía IQR (1.5x)",
        ))
    return result, metrics


def transform_customers(
    raw_df: pd.DataFrame, channel_reference: pd.DataFrame, metadata_path
) -> tuple[pd.DataFrame, list[QualityMetric]]:
    """Limpia, enriquece y segmenta los registros de campañas bancarias."""
    df = raw_df.copy().drop_duplicates().reset_index(drop=True)

    numeric_columns = ["age", "balance", "day", "duration", "campaign", "pdays", "previous"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

    text_columns = ["job", "marital", "education", "default", "housing", "loan", "contact", "month", "poutcome", "y"]
    for column in text_columns:
        df[column] = df[column].astype(str).str.strip().str.lower()

    df, outlier_metrics = cap_outliers_iqr(df, OUTLIER_COLUMNS)

    df.insert(0, "customer_id", range(1, len(df) + 1))
    df["conversion_flag"] = (df["y"] == "yes").astype(int)
    df["duration_minutes"] = (df["duration"] / 60).round(2)
    df["month_number"] = df["month"].map(MONTH_ORDER)
    df["pdays_for_model"] = df["pdays"].where(df["pdays"] >= 0, 0)
    df["had_previous_contact"] = (df["previous"] > 0).astype(int)

    df["age_group"] = pd.cut(
        df["age"], bins=[0, 29, 39, 49, 59, 200],
        labels=["18-29", "30-39", "40-49", "50-59", "60+"],
        include_lowest=True,
    ).astype(str)
    df["balance_level"] = pd.cut(
        df["balance"], bins=[-float("inf"), 0, 1000, 5000, float("inf")],
        labels=["debt_or_zero", "low", "medium", "high"],
        include_lowest=True,
    ).astype(str)

    df = df.merge(channel_reference, on="contact", how="left", validate="many_to_one")
    if df["channel_label"].isna().any():
        raise ValueError("Existen canales de contacto sin correspondencia en la fuente SQL")

    segmented = add_customer_segments(df, metadata_path)
    return segmented, outlier_metrics


def build_segment_summary(customers: pd.DataFrame) -> pd.DataFrame:
    return (
        customers.groupby("customer_segment", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            conversion_rate=("conversion_flag", "mean"),
            average_age=("age", "mean"),
            average_balance=("balance", "mean"),
            average_duration_minutes=("duration_minutes", "mean"),
            average_campaign_contacts=("campaign", "mean"),
        )
        .assign(conversion_rate=lambda frame: (frame["conversion_rate"] * 100).round(2))
        .round({"average_age": 2, "average_balance": 2, "average_duration_minutes": 2, "average_campaign_contacts": 2})
    )


def build_job_marital_profile(customers: pd.DataFrame) -> pd.DataFrame:
    """Perfil por ocupación y estado civil: agrupación multi-clave con múltiples agregaciones."""
    return (
        customers.groupby(["job", "marital"], as_index=False)
        .agg(
            customers=("customer_id", "count"),
            balance_mean=("balance", "mean"),
            balance_median=("balance", "median"),
            duration_minutes_mean=("duration_minutes", "mean"),
            conversion_rate=("conversion_flag", "mean"),
        )
        .assign(conversion_rate=lambda frame: (frame["conversion_rate"] * 100).round(2))
        .round({"balance_mean": 2, "balance_median": 2, "duration_minutes_mean": 2})
        .sort_values(["job", "marital"])
        .reset_index(drop=True)
    )


def build_conversion_pivot(customers: pd.DataFrame) -> pd.DataFrame:
    """Tasa de conversión (%) por mes y grupo de canal, vía pivot_table (reshape ancho)."""
    pivot = pd.pivot_table(
        customers,
        values="conversion_flag",
        index="month",
        columns="channel_group",
        aggfunc="mean",
        fill_value=0.0,
    )
    pivot = (pivot * 100).round(2)
    pivot["month_number"] = pivot.index.map(MONTH_ORDER)
    pivot = pivot.sort_values("month_number").drop(columns="month_number")
    return pivot.reset_index().rename_axis(columns=None)
