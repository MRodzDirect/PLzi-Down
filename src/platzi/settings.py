import json
from pathlib import Path

from pydantic import BaseModel, Field

from .constants import SETTINGS_FILE


class ProxySettings(BaseModel):
    enabled: bool = False
    pool: list[str] = Field(default_factory=list)
    rotation_seconds: int = 300
    browser_enabled: bool = True


class AppSettings(BaseModel):
    proxy: ProxySettings = Field(default_factory=ProxySettings)


def load_settings(path: str | Path = SETTINGS_FILE) -> AppSettings:
    settings_path = path if isinstance(path, Path) else Path(path)
    if not settings_path.exists():
        return AppSettings()

    try:
        with open(settings_path, "r", encoding="utf-8") as file:
            raw = json.load(file)
        return AppSettings.model_validate(raw)
    except Exception:
        return AppSettings()


def save_settings(settings: AppSettings, path: str | Path = SETTINGS_FILE) -> None:
    settings_path = path if isinstance(path, Path) else Path(path)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as file:
        json.dump(settings.model_dump(), file, indent=4, ensure_ascii=False)
