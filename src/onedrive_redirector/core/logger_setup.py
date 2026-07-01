from __future__ import annotations

import logging
from pathlib import Path

from .settings_store import get_appdata_root


def setup_logging(appdata_root: Path | None = None) -> Path:
    root = appdata_root or get_appdata_root()
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "app.log"

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
