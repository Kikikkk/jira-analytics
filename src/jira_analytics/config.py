import configparser
from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    """Ошибка чтения конфигурационного файла."""


@dataclass(frozen=True)
class Config:
    base_url: str
    project: str
    page_size: int
    retries: int
    timeout: int
    output_dir: Path
    bins: int
    max_days: float | None


def load_config(path: str) -> Config:
    """Читает config.ini и возвращает типизированные настройки."""
    parser = configparser.ConfigParser()
    if not parser.read(path, encoding="utf-8"):
        raise ConfigError(f"Не удалось прочитать конфиг: {path}")
    try:
        max_days_raw = parser.get("plots", "max_days", fallback="").strip()
        return Config(
            base_url=parser.get("jira", "base_url"),
            project=parser.get("jira", "project"),
            page_size=parser.getint("jira", "page_size", fallback=50),
            retries=parser.getint("jira", "retries", fallback=3),
            timeout=parser.getint("jira", "timeout", fallback=30),
            output_dir=Path(parser.get("output", "directory", fallback="output")),
            bins=parser.getint("plots", "bins", fallback=50),
            max_days=float(max_days_raw) if max_days_raw else None,
        )
    except (configparser.Error, ValueError) as exc:
        raise ConfigError(f"Некорректный конфиг {path}: {exc}") from exc