from pathlib import Path
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from path_utils import resource_path, user_data_path


REQUIRED_ASSETS = ("idle", "press_left", "press_right", "sleep", "wow", "smile", "happy", "sad")

PROCESSED_FILES = {
    "idle": "bear_peek_idle.png",
    "press_left": "bear_peek_press_left.png",
    "press_right": "bear_peek_press_right.png",
    "sleep": "bear_peek_sleep.png",
    "wow": "bear_peek_wow.png",
    "smile": "bear_peek_smile.png",
    "happy": "bear_peek_happy.png",
    "sad": "bear_peek_sad.png",
}

RAW_FILES = {
    "idle": "bear_idle.png",
    "press_left": "bear_press_left.png",
    "press_right": "bear_press_right.png",
    "sleep": "bear_sleep.png",
    "wow": "bear_wow.png",
    "smile": "bear_smile.png",
    "happy": "bear_happy.png",
    "sad": "bear_sad.png",
}


def _asset_roots():
    return [
        resource_path("assets/processed"),
        user_data_path("assets/processed"),
        resource_path("yier_assets"),
        resource_path("assets"),
    ]


def _find_state_asset(state):
    for root in _asset_roots():
        for name in (PROCESSED_FILES[state], RAW_FILES[state]):
            path = root / name
            if path.exists():
                return path
    return None


def _prepare_missing_source_assets():
    """Source-mode fallback only; frozen builds use bundled processed PNGs."""
    if getattr(sys, "frozen", False):
        return {}
    try:
        from asset_generator import ASSETS_DIR, generate_assets

        return generate_assets(ASSETS_DIR, overwrite=False)
    except Exception as exc:
        print(f"[KeyBear] source asset fallback skipped: {exc}")
        return {}


class CatWidget(QWidget):
    """Displays one complete bear state image without positional animation."""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.state = "idle"
        self.pixmaps = {}
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.load_assets()
        self.apply_settings()

    def load_assets(self):
        self.pixmaps.clear()
        resolved = {}
        idle_path = _find_state_asset("idle")
        if idle_path is None:
            resolved = _prepare_missing_source_assets()
            idle_path = resolved.get("idle")
        for state in REQUIRED_ASSETS:
            path = _find_state_asset(state) or resolved.get(state) or idle_path
            if path is None or not Path(path).exists():
                print(f"[KeyBear] missing bear state image: {state}; using idle")
                path = idle_path
            self.pixmaps[state] = QPixmap(str(path))

    def apply_settings(self):
        size = int(self.settings.get("cat_size") * self.settings.get("overall_scale") * self.settings.get("bear_scale"))
        self.setFixedSize(size, int(size * 0.86))

    def set_state(self, state):
        if state not in self.pixmaps:
            print(f"[KeyBear] missing state {state}; using idle")
            state = "idle"
        if self.state != state:
            self.state = state
            self.update()
            if hasattr(self.parent(), "update_layering"):
                self.parent().update_layering()

    def set_press_state(self, side):
        self.set_state("press_left" if side == "left" else "press_right")

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        pixmap = self.pixmaps.get(self.state) or self.pixmaps["idle"]
        painter.drawPixmap(0, 0, self.width(), self.height(), pixmap)
