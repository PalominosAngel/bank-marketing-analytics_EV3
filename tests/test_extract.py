from pathlib import Path
import json
import pandas as pd

from etl.config import Settings
from etl.extract import extract_bank_csv, extract_world_bank_indicators


class FailingSession:
    def get(self, *args, **kwargs):
        import requests
        raise requests.ConnectionError("sin conexión")


def test_extract_csv_reads_rows(tmp_path: Path):
    path = tmp_path / "sample.csv"
    path.write_text("age,job\n30,services\n", encoding="utf-8")
    frame = extract_bank_csv(path)
    assert len(frame) == 1


def test_external_api_uses_cache_when_network_fails(tmp_path: Path):
    cache = tmp_path / "cache.json"
    cache.write_text(json.dumps({
        "retrieved_at": "demo",
        "rows": [{"country_code": "PRT", "year": 2024, "indicator_code": "TEST", "indicator_name": "demo", "value": 1.0, "source_type": "cache"}]
    }), encoding="utf-8")
    settings = Settings(world_bank_cache_path=cache, world_bank_max_retries=1)
    result = extract_world_bank_indicators(settings, session=FailingSession())
    assert result.source_status == "cache_fallback"
    assert len(result.data) == 1
