from pathlib import Path
import pandas as pd

from etl.transform import (
    build_conversion_pivot,
    build_job_marital_profile,
    build_segment_summary,
    cap_outliers_iqr,
    transform_customers,
)


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
    # Outlier deliberado para ejercitar el capado IQR
    rows.append({
        "age": 40, "job": "management", "marital": "single", "education": "tertiary",
        "default": "no", "balance": 999_999, "housing": "yes", "loan": "no", "contact": "cellular",
        "day": 10, "month": "may", "duration": 60, "campaign": 1,
        "pdays": -1, "previous": 0, "poutcome": "unknown", "y": "no",
    })
    return pd.DataFrame(rows)


def reference_frame():
    return pd.DataFrame([{"contact": "cellular", "channel_label": "Teléfono celular", "channel_group": "digital", "priority_order": 1}])


def test_transform_adds_business_and_clustering_columns(tmp_path: Path):
    transformed, metrics = transform_customers(raw_frame(), reference_frame(), tmp_path / "metadata.json")
    required = {"customer_id", "conversion_flag", "duration_minutes", "age_group", "customer_segment", "pca_component_1", "pca_component_2"}
    assert required.issubset(transformed.columns)
    assert (tmp_path / "metadata.json").exists()
    assert any(metric.metric == "balance_outliers_capped" for metric in metrics)


def test_transform_caps_the_deliberate_balance_outlier(tmp_path: Path):
    transformed, _ = transform_customers(raw_frame(), reference_frame(), tmp_path / "metadata.json")
    assert transformed["balance"].max() < 999_999


def test_segment_summary_is_generated(tmp_path: Path):
    transformed, _ = transform_customers(raw_frame(), reference_frame(), tmp_path / "metadata.json")
    summary = build_segment_summary(transformed)
    assert not summary.empty
    assert "conversion_rate" in summary.columns


def test_cap_outliers_iqr_clips_values_and_reports_affected_count():
    frame = pd.DataFrame({"balance": [10, 20, 30, 40, 5000]})
    capped, metrics = cap_outliers_iqr(frame, ["balance"])
    assert capped["balance"].max() < 5000
    assert metrics[0].value == 1


def test_build_job_marital_profile_groups_by_two_keys(tmp_path: Path):
    transformed, _ = transform_customers(raw_frame(), reference_frame(), tmp_path / "metadata.json")
    profile = build_job_marital_profile(transformed)
    assert {"job", "marital", "conversion_rate", "balance_mean", "balance_median"}.issubset(profile.columns)
    assert len(profile) == transformed.groupby(["job", "marital"]).ngroups


def test_build_conversion_pivot_reshapes_month_by_channel(tmp_path: Path):
    transformed, _ = transform_customers(raw_frame(), reference_frame(), tmp_path / "metadata.json")
    pivot = build_conversion_pivot(transformed)
    assert "month" in pivot.columns
    assert "digital" in pivot.columns
