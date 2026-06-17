from pathlib import Path
import pandas as pd

from etl.transform import transform_customers, build_segment_summary


def raw_frame():
    rows = []
    for i in range(12):
        rows.append({
            "age": 25 + i, "job": "management" if i % 2 == 0 else "services",
            "marital": "single", "education": "tertiary", "default": "no",
            "balance": 100 * i, "housing": "yes", "loan": "no", "contact": "cellular",
            "day": 10, "month": "may", "duration": 60 + i * 10, "campaign": 1 + i % 3,
            "pdays": -1 if i % 2 else 20, "previous": i % 4, "poutcome": "unknown",
            "y": "yes" if i % 3 == 0 else "no",
        })
    return pd.DataFrame(rows)


def reference_frame():
    return pd.DataFrame([{ "contact": "cellular", "channel_label": "Teléfono celular", "channel_group": "digital", "priority_order": 1 }])


def test_transform_adds_business_and_clustering_columns(tmp_path: Path):
    transformed = transform_customers(raw_frame(), reference_frame(), tmp_path / "metadata.json")
    required = {"customer_id", "conversion_flag", "duration_minutes", "age_group", "customer_segment", "pca_component_1", "pca_component_2"}
    assert required.issubset(transformed.columns)
    assert (tmp_path / "metadata.json").exists()


def test_segment_summary_is_generated(tmp_path: Path):
    transformed = transform_customers(raw_frame(), reference_frame(), tmp_path / "metadata.json")
    summary = build_segment_summary(transformed)
    assert not summary.empty
    assert "conversion_rate" in summary.columns
