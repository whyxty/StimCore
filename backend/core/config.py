"""Загрузка профиля месторождения (config.json) — переиспользуем из старого проекта."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEGACY_CONFIG = ROOT / "sko_calculator" / "config.json"


def load_default_config() -> dict:
    """Грузит дефолтный профиль (Предкарпатье) из старого Streamlit-проекта."""
    if LEGACY_CONFIG.exists():
        return json.loads(LEGACY_CONFIG.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Не найден config.json: {LEGACY_CONFIG}")
