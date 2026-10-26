"""Сборка дистрибутива: python scripts/build.py

Создаёт dist/jira-analytics-<версия>.zip с кодом, конфигом,
зависимостями, README и скриптами запуска.
"""
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "dist"
PACKAGE_NAME = "jira-analytics"
VERSION_FILE = ROOT / "src" / PACKAGE_NAME.replace("-", "_") / "__init__.py"

# (откуда в репозитории, куда в архиве)
STATIC_FILES = [
    ("config.ini", "config.ini"),
    ("requirements.txt", "requirements.txt"),
    ("README.md", "README.md"),
    ("scripts/run.bat", "run.bat"),
    ("scripts/run.sh", "run.sh"),
]


def read_version() -> str:
    """Читает __version__ из пакета, чтобы версия хранилась в одном месте."""
    match = re.search(r'__version__\s*=\s*"([^"]+)"', VERSION_FILE.read_text(encoding="utf-8"))
    if not match:
        raise RuntimeError(f"Не найден __version__ в {VERSION_FILE}")
    return match.group(1)


def collect_files() -> list[tuple[Path, str]]:
    """Список (исходный файл, путь внутри архива). Проверяет, что всё на месте."""
    files = [(ROOT / src, dst) for src, dst in STATIC_FILES]
    for path in sorted((ROOT / "src").rglob("*.py")):
        files.append((path, path.relative_to(ROOT).as_posix()))
    missing = [str(src) for src, _ in files if not src.is_file()]
    if missing:
        raise FileNotFoundError("Не найдены файлы для сборки: " + ", ".join(missing))
    return files


def build() -> Path:
    """Собирает zip-архив дистрибутива и возвращает путь к нему."""
    version = read_version()
    folder = f"{PACKAGE_NAME}-{version}"
    DIST_DIR.mkdir(exist_ok=True)
    archive = DIST_DIR / f"{folder}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, dst in collect_files():
            zf.write(src, f"{folder}/{dst}")
    return archive


if __name__ == "__main__":
    print(f"Собрано: {build()}")