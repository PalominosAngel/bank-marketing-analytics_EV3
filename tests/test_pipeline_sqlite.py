from pathlib import Path
import pandas as pd

from etl.database import DatabaseManager


def test_sqlite_reference_source_is_seeded(tmp_path: Path):
    db = DatabaseManager(f"sqlite:///{tmp_path / 'test.db'}")
    db.initialize_schema()
    reference = db.read_sql("SELECT * FROM contact_channel_reference")
    assert set(reference["contact"]) == {"cellular", "telephone", "unknown"}
