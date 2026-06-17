"""Acceso de lectura a las tablas publicadas por el ETL."""
from __future__ import annotations

import os
from etl.database import DatabaseManager

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/database/bank_analytics.db")
db = DatabaseManager(DATABASE_URL)
