"""Cliente HTTP del dashboard para consumir la API propia."""
from __future__ import annotations

import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def get_json(path: str, params: dict | None = None):
    response = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=8)
    response.raise_for_status()
    return response.json()
