import os
import sys
from pathlib import Path


APP_NAME = "KeyBearCompanion"


def resource_root():
    """Return the directory that contains bundled read-only resources."""

    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def resource_path(relative_path):
    """Resolve a bundled resource path in source and PyInstaller modes."""

    return resource_root() / Path(relative_path)


def user_data_dir():
    """Return a writable per-user directory for settings and generated files."""

    appdata = os.environ.get("APPDATA")
    if appdata:
        candidate = Path(appdata) / APP_NAME
    else:
        candidate = Path.home() / "AppData" / "Roaming" / APP_NAME
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate
    except OSError:
        fallback = Path.cwd() / "user_data" / APP_NAME
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def user_data_path(relative_path):
    return user_data_dir() / Path(relative_path)
