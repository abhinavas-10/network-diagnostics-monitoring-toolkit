from datetime import datetime, timezone
from pathlib import Path
import logging

def timestamp() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def setup_logging(log_dir: str = "logs", level: str = "INFO") -> logging.Logger:
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("network_toolkit")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        file_handler = logging.FileHandler(path / "network_toolkit.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console)
    return logger
