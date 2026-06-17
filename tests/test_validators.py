import pandas as pd
import pytest

from etl.validators import validate_bank_schema


def valid_frame():
    return pd.DataFrame([{ 
        "age": 35, "job": "management", "marital": "single", "education": "tertiary",
        "default": "no", "balance": 1000, "housing": "yes", "loan": "no",
        "contact": "cellular", "day": 10, "month": "may", "duration": 120,
        "campaign": 1, "pdays": -1, "previous": 0, "poutcome": "unknown", "y": "no"
    }])


def test_valid_schema_returns_quality_metrics():
    metrics = validate_bank_schema(valid_frame())
    assert any(metric.metric == "rows_received" for metric in metrics)


def test_missing_column_fails_fast():
    frame = valid_frame().drop(columns=["age"])
    with pytest.raises(ValueError, match="Faltan columnas obligatorias"):
        validate_bank_schema(frame)


def test_invalid_binary_domain_fails_fast():
    frame = valid_frame()
    frame.loc[0, "y"] = "maybe"
    with pytest.raises(ValueError, match="valores no permitidos"):
        validate_bank_schema(frame)
