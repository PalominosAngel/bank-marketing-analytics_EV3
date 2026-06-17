"""Extracción desde CSV, API REST externa y tabla SQL de referencia."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import time

import pandas as pd
import requests

from etl.config import Settings
from etl.database import DatabaseManager


INDICATORS = {
    "SL.UEM.TOTL.ZS": "unemployment_total_pct",
    "FP.CPI.TOTL.ZG": "inflation_consumer_prices_pct",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
}


@dataclass
class ApiExtractionResult:
    data: pd.DataFrame
    source_status: str
    retrieved_at: str


def extract_bank_csv(path: Path) -> pd.DataFrame:
    """Lee el CSV principal y falla explícitamente si no existe o está vacío."""
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo CSV requerido: {path}")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("El archivo bank.csv no contiene registros")
    return df


def extract_channel_reference(db: DatabaseManager) -> pd.DataFrame:
    """Extrae una tercera fuente desde SQL: catálogo de canales de contacto."""
    df = db.read_sql("SELECT contact, channel_label, channel_group, priority_order FROM contact_channel_reference")
    if df.empty:
        raise ValueError("La tabla SQL contact_channel_reference está vacía")
    return df


def _api_url(settings: Settings, indicator: str) -> str:
    return (
        f"{settings.world_bank_api_base_url}/country/{settings.world_bank_country}"
        f"/indicator/{indicator}?format=json"
        f"&date={settings.world_bank_start_year}:{settings.world_bank_end_year}&per_page=100"
    )


def _normalize_world_bank_payload(payload: list, indicator: str, indicator_name: str) -> list[dict]:
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise ValueError(f"Respuesta inesperada de World Bank API para {indicator}")
    rows = []
    for item in payload[1]:
        value = item.get("value")
        year = item.get("date")
        if year is None:
            continue
        rows.append({
            "country_code": item.get("countryiso3code", "PRT"),
            "year": int(year),
            "indicator_code": indicator,
            "indicator_name": indicator_name,
            "value": value,
            "source_type": "world_bank_api",
        })
    return rows


def _read_cache(path: Path) -> ApiExtractionResult:
    if not path.exists():
        raise FileNotFoundError("No existe caché de respaldo para la API externa")
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    if not rows:
        raise ValueError("El caché de respaldo de la API está vacío")
    return ApiExtractionResult(
        data=pd.DataFrame(rows),
        source_status="cache_fallback",
        retrieved_at=payload.get("retrieved_at", "unknown"),
    )


def extract_world_bank_indicators(settings: Settings, session: requests.Session | None = None) -> ApiExtractionResult:
    """Consume la API con reintentos y utiliza un caché si la red falla."""
    session = session or requests.Session()
    all_rows: list[dict] = []
    try:
        for indicator, indicator_name in INDICATORS.items():
            last_error: Exception | None = None
            for attempt in range(1, settings.world_bank_max_retries + 1):
                try:
                    response = session.get(_api_url(settings, indicator), timeout=settings.world_bank_timeout_seconds)
                    response.raise_for_status()
                    all_rows.extend(_normalize_world_bank_payload(response.json(), indicator, indicator_name))
                    last_error = None
                    break
                except (requests.RequestException, ValueError) as exc:
                    last_error = exc
                    if attempt < settings.world_bank_max_retries:
                        time.sleep(min(2 ** (attempt - 1), 4))
            if last_error is not None:
                raise last_error

        retrieved_at = datetime.now(timezone.utc).isoformat()
        settings.world_bank_cache_path.parent.mkdir(parents=True, exist_ok=True)
        settings.world_bank_cache_path.write_text(
            json.dumps({"retrieved_at": retrieved_at, "rows": all_rows}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return ApiExtractionResult(pd.DataFrame(all_rows), "live_api", retrieved_at)
    except Exception:
        return _read_cache(settings.world_bank_cache_path)
