import os
from pathlib import Path
import importlib
import pandas as pd
from fastapi.testclient import TestClient

from etl.database import DatabaseManager


def test_health_endpoint(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'api.db'}")
    import api.database
    import api.main
    importlib.reload(api.database)
    importlib.reload(api.main)
    client = TestClient(api.main.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_model_metrics_endpoint_returns_404_when_not_trained(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'api.db'}")
    import api.database
    import api.main
    importlib.reload(api.database)
    importlib.reload(api.main)
    monkeypatch.setattr(api.main, "MODEL_METRICS_PATH", tmp_path / "missing_metrics.json")

    client = TestClient(api.main.app)
    response = client.get("/models/metrics")
    assert response.status_code == 404


def test_model_metrics_endpoint_returns_saved_metrics(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'api.db'}")
    import api.database
    import api.main
    importlib.reload(api.database)
    importlib.reload(api.main)

    metrics_path = tmp_path / "metrics.json"
    metrics_path.write_text('{"best_model": "logistic_regression", "models": {}}', encoding="utf-8")
    monkeypatch.setattr(api.main, "MODEL_METRICS_PATH", metrics_path)

    client = TestClient(api.main.app)
    response = client.get("/models/metrics")
    assert response.status_code == 200
    assert response.json()["best_model"] == "logistic_regression"


def test_job_marital_profile_and_conversion_pivot_endpoints(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'api.db'}")
    import api.database
    import api.main
    importlib.reload(api.database)
    importlib.reload(api.main)

    api.database.db.replace_table(
        pd.DataFrame([{"job": "management", "marital": "single", "customers": 3, "balance_mean": 100.0, "balance_median": 90.0, "duration_minutes_mean": 4.0, "conversion_rate": 12.5}]),
        "job_marital_profile",
    )
    api.database.db.replace_table(
        pd.DataFrame([{"month": "may", "digital": 10.5, "traditional": 8.0, "unknown": 0.0}]),
        "conversion_pivot_by_month_channel",
    )

    client = TestClient(api.main.app)
    profile_response = client.get("/api/profile/job-marital")
    pivot_response = client.get("/api/conversion-pivot")

    assert profile_response.status_code == 200
    assert profile_response.json()[0]["job"] == "management"
    assert pivot_response.status_code == 200
    assert pivot_response.json()[0]["month"] == "may"
