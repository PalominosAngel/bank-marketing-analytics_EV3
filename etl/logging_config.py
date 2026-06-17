"""Configuración de logging profesional para scripts ETL y servicios."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(level: str = "INFO", log_file: str = "logs/pipeline.log") -> logging.Logger:
    """Configura consola y archivo rotativo sin duplicar handlers."""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("bank_analytics")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger
