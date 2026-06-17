"""Transformaciones de negocio reproducibles."""
from __future__ import annotations

import pandas as pd

from etl.clustering import add_customer_segments


MONTH_ORDER = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def transform_customers(raw_df: pd.DataFrame, channel_reference: pd.DataFrame, metadata_path) -> pd.DataFrame:
    """Limpia, enriquece y segmenta los registros de campañas bancarias."""
    df = raw_df.copy().drop_duplicates().reset_index(drop=True)

    numeric_columns = ["age", "balance", "day", "duration", "campaign", "pdays", "previous"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

    text_columns = ["job", "marital", "education", "default", "housing", "loan", "contact", "month", "poutcome", "y"]
    for column in text_columns:
        df[column] = df[column].astype(str).str.strip().str.lower()

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

    return add_customer_segments(df, metadata_path)


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
