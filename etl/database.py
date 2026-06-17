"""Abstracción mínima de base de datos con SQLite local por defecto."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Any
import sqlite3

import pandas as pd


class DatabaseManager:
    """Gestiona conexiones, tablas y cargas transaccionales.

    La configuración por defecto utiliza SQLite para simplificar la instalación
    y permitir una ejecución reproducible sin servidores externos.
    """

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.is_sqlite = database_url.startswith("sqlite:///")
        self._engine = None

    def _sqlite_path(self) -> Path:
        path = Path(self.database_url.removeprefix("sqlite:///"))
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _get_engine(self):
        if self._engine is None:
            try:
                from sqlalchemy import create_engine
            except ImportError as exc:
                raise RuntimeError(
                    "Para utilizar una base SQL externa instala las dependencias con: pip install -r requirements.txt"
                ) from exc
            self._engine = create_engine(self.database_url, pool_pre_ping=True, future=True)
        return self._engine

    @contextmanager
    def connect(self) -> Iterator[Any]:
        if self.is_sqlite:
            conn = sqlite3.connect(self._sqlite_path())
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        else:
            engine = self._get_engine()
            with engine.begin() as conn:
                yield conn

    def initialize_schema(self) -> None:
        """Crea las tablas de control y la tabla SQL de referencia."""
        statements = [
            """
            CREATE TABLE IF NOT EXISTS contact_channel_reference (
                contact VARCHAR(30) PRIMARY KEY,
                channel_label VARCHAR(80) NOT NULL,
                channel_group VARCHAR(40) NOT NULL,
                priority_order INTEGER NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS etl_runs (
                run_id VARCHAR(50) PRIMARY KEY,
                started_at VARCHAR(40) NOT NULL,
                finished_at VARCHAR(40),
                status VARCHAR(20) NOT NULL,
                rows_extracted INTEGER DEFAULT 0,
                rows_loaded INTEGER DEFAULT 0,
                api_source_status VARCHAR(40),
                error_message TEXT
            )
            """,
        ]
        with self.connect() as conn:
            for statement in statements:
                self.execute(conn, statement)
        self.seed_reference_data()

    def seed_reference_data(self) -> None:
        rows = [
            ("cellular", "Teléfono celular", "digital", 1),
            ("telephone", "Teléfono fijo", "traditional", 2),
            ("unknown", "Canal no informado", "unknown", 3),
        ]
        with self.connect() as conn:
            if self.is_sqlite:
                conn.executemany(
                    "INSERT OR IGNORE INTO contact_channel_reference (contact, channel_label, channel_group, priority_order) VALUES (?, ?, ?, ?)",
                    rows,
                )
            else:
                from sqlalchemy import text
                for row in rows:
                    conn.execute(text("""
                        INSERT INTO contact_channel_reference (contact, channel_label, channel_group, priority_order)
                        VALUES (:contact, :label, :grp, :priority)
                        ON CONFLICT (contact) DO NOTHING
                    """), {"contact": row[0], "label": row[1], "grp": row[2], "priority": row[3]})

    def read_sql(self, query: str, params: dict | None = None) -> pd.DataFrame:
        with self.connect() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def replace_table(self, df: pd.DataFrame, table_name: str) -> None:
        """Reemplaza una tabla usando una transacción controlada."""
        with self.connect() as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)

    def append_table(self, df: pd.DataFrame, table_name: str) -> None:
        with self.connect() as conn:
            df.to_sql(table_name, conn, if_exists="append", index=False)

    def execute(self, conn: Any, statement: str, params: dict | tuple | None = None) -> None:
        params = params or {}
        if self.is_sqlite:
            conn.execute(statement, params)
        else:
            from sqlalchemy import text
            conn.execute(text(statement), params)

    def upsert_etl_run(self, record: dict) -> None:
        columns = [
            "run_id", "started_at", "finished_at", "status", "rows_extracted",
            "rows_loaded", "api_source_status", "error_message"
        ]
        values = [record.get(column) for column in columns]
        with self.connect() as conn:
            if self.is_sqlite:
                placeholders = ",".join("?" for _ in columns)
                conn.execute(
                    f"INSERT OR REPLACE INTO etl_runs ({','.join(columns)}) VALUES ({placeholders})",
                    values,
                )
            else:
                from sqlalchemy import text
                conn.execute(text("""
                    INSERT INTO etl_runs (
                        run_id, started_at, finished_at, status, rows_extracted,
                        rows_loaded, api_source_status, error_message
                    ) VALUES (
                        :run_id, :started_at, :finished_at, :status, :rows_extracted,
                        :rows_loaded, :api_source_status, :error_message
                    )
                    ON CONFLICT (run_id) DO UPDATE SET
                        finished_at = EXCLUDED.finished_at,
                        status = EXCLUDED.status,
                        rows_extracted = EXCLUDED.rows_extracted,
                        rows_loaded = EXCLUDED.rows_loaded,
                        api_source_status = EXCLUDED.api_source_status,
                        error_message = EXCLUDED.error_message
                """), record)
