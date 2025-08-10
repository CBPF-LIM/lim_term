import os
from ..config import CAPTURE_DIR


def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def ensure_capture_dir() -> str:
    ensure_dir(CAPTURE_DIR)
    return CAPTURE_DIR
