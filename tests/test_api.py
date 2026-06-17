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
