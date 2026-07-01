from __future__ import annotations

import logging
from pathlib import Path

from .constants import LOG_DIR_NAME, LOG_FILE_NAME, get_appdata_root
from .file_ops import ensure_directory


def setup_logging(appdata_root: Path | None = None) -> Path:
    root = appdata_root or get_appdata_root()
    log_dir = ensure_directory(root / LOG_DIR_NAME)
    log_path = log_dir / LOG_FILE_NAME

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    logging.getLogger(__name__).info("Application logging initialized.")
    return log_path

