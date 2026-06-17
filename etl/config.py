"""Configuración centralizada del pipeline ETL."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Variables externas necesarias para ejecutar el proyecto."""

    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/database/bank_analytics.db")
    bank_csv_path: Path = Path(os.getenv("BANK_CSV_PATH", "data/raw/bank.csv"))
    world_bank_api_base_url: str = os.getenv("WORLD_BANK_API_BASE_URL", "https://api.worldbank.org/v2")
    world_bank_country: str = os.getenv("WORLD_BANK_COUNTRY", "PRT")
    world_bank_start_year: int = int(os.getenv("WORLD_BANK_START_YEAR", "2018"))
    world_bank_end_year: int = int(os.getenv("WORLD_BANK_END_YEAR", "2024"))
    world_bank_timeout_seconds: int = int(os.getenv("WORLD_BANK_TIMEOUT_SECONDS", "8"))
    world_bank_max_retries: int = int(os.getenv("WORLD_BANK_MAX_RETRIES", "3"))
    world_bank_cache_path: Path = Path(os.getenv("WORLD_BANK_CACHE_PATH", "data/cache/world_bank_indicators_cache.json"))


settings = Settings()
