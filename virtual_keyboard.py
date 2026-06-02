import os

from keyboard_layout import KeyboardLayout
from path_utils import resource_path, user_data_path


YIER_KEYBOARD_PATH = resource_path("yier_assets/keyboard.png")
LEGACY_YIER_KEYBOARD_PATH = resource_path("一二形象/键盘.png")
PROCESSED_KEYBOARD_PATH = resource_path("assets/processed/keyboard.png")
WRITABLE_PROCESSED_KEYBOARD_PATH = user_data_path("assets/processed/keyboard.png")
KEYBOARD_IMAGE_CANDIDATES = [
    YIER_KEYBOARD_PATH,
    LEGACY_YIER_KEYBOARD_PATH,
    resource_path("assets/keyboard.png"),
    PROCESSED_KEYBOARD_PATH,
    WRITABLE_PROCESSED_KEYBOARD_PATH,
]

KEY_OUTLINE_MODE = "minimal"
HIDE_KEY_TEXT = os.environ.get("KEYBEAR_HIDE_KEY_TEXT") == "1"
HIDE_KEY_OUTLINE = os.environ.get("KEYBEAR_HIDE_KEY_OUTLINE") == "1"
KEY_TYPE_DEBUG = os.environ.get("KEYBEAR_KEY_TYPE_DEBUG") == "1"

KEYBOARD_THEMES = {
    "dark_keycaps": {
        "normal_fill": "#6B422E",
        "special_fill": "#7A4A36",
        "tray_fill": "#FFF6E8",
        "border": "#8A6248",
        "special_border": "#9B7058",
        "border_alpha": 150,
        "special_border_alpha": 165,
        "text": "#FFF3DE",
        "pressed_fill": "#D99472",
        "pressed_text": "#FFFFFF",
        "pressed_alpha": 170,
        "tray_pen": "#DCC5AA",
        "tray_pen_alpha": 135,
        "shadow": False,
    },
    "light_keycaps": {
        "normal_fill": "#FFF8EA",
        "special_fill": "#FFE8E3",
        "tray_fill": "#FFF6E8",
        "border": "#E4CDB4",
        "special_border": "#E7B8AE",
        "border_alpha": 105,
        "special_border_alpha": 125,
        "text": "#FFF3DE",
        "pressed_fill": "#F6B6A8",
        "pressed_text": "#FFFFFF",
        "pressed_alpha": 120,
        "tray_pen": "#DCC5AA",
        "tray_pen_alpha": 115,
        "shadow": False,
    },
    "debug_key_types": {
        "normal_fill": "#FFFF00",
        "special_fill": "#00AAFF",
        "tray_fill": "#FFFFFF",
        "border": "#111111",
        "special_border": "#111111",
        "border_alpha": 160,
        "special_border_alpha": 160,
        "text": "#000000",
        "pressed_fill": "#FF0000",
        "pressed_text": "#FFFFFF",
        "pressed_alpha": 210,
        "tray_pen": "#00AAFF",
        "tray_pen_alpha": 120,
        "shadow": False,
    },
}

DEBUG_KEY_IDS = {
    "Q",
    "A",
    "1",
    "Space",
    "Tab",
    "Caps",
    "LeftShift",
    "RightShift",
    "Enter",
    "Backspace",
    "LeftCtrl",
    "RightCtrl",
    "LeftAlt",
    "RightAlt",
}


def find_keyboard_image():
    for path in KEYBOARD_IMAGE_CANDIDATES:
        if path.exists():
            return path
    return None


try:
    from PySide6.QtCore import QRect, QRectF, Qt, Signal
    from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap
    from PySide6.QtWidgets import QWidget

    class VirtualKeyboard(QWidget):
        key_pressed = Signal(str)
        key_released = Signal(str)

        def __init__(self, settings, parent=None):
            super().__init__(parent)
            self.settings = settings
            self.layout_model = KeyboardLayout()
            self.pressed = set()
            self.keyboard_pixmap = QPixmap()
            self.keyboard_image_path = None
            self.using_fallback = False
            self._printed_generated_palette = False
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.apply_settings()

        def apply_settings(self):
            self.layout_model = KeyboardLayout(
                self.settings.get("keyboard_layout"),
                self.settings.get("keyboard_density", "clean"),
            )
            self.keyboard_pixmap = QPixmap()
            self.keyboard_image_path = None
            self.using_fallback = self.settings.get("keyboard_style") == "生成键盘"

            scale = self.settings.get("keyboard_scale") * self.settings.get("overall_scale")
            target_w = int(560 * scale)
            if self.settings.get("keyboard_style") == "图片键盘":
                self._ensure_processed_keyboard()
                self.keyboard_image_path = find_keyboard_image()
                self.using_fallback = self.keyboard_image_path is None
                if self.keyboard_image_path:
                    self.keyboard_pixmap = QPixmap(str(self.keyboard_image_path))
                    aspect = self.keyboard_pixmap.height() / max(1, self.keyboard_pixmap.width())
                    self.setFixedSize(target_w, max(80, int(target_w * aspect)))
                else:
                    self.setFixedSize(target_w, int(310 * scale))
            else:
                self.setFixedSize(target_w, int(310 * scale))

            self._print_debug_info()
            self.update()

        def _ensure_processed_keyboard(self):
            if YIER_KEYBOARD_PATH.exists():
                try:
                    from transparent_processor import process_keyboard

                    process_keyboard(overwrite=True)
                except Exception as exc:
                    print(f"[KeyBear] Failed to process keyboard transparency: {exc}")

        def _print_debug_info(self):
            loaded = self.keyboard_image_path
            try:
                loaded = loaded if loaded else None
            except ValueError:
                pass
            from pathlib import Path

            print(f"[KeyBear] Current working directory: {Path.cwd()}")
            print(f"[KeyBear] Found yier_assets/keyboard.png: {YIER_KEYBOARD_PATH.exists()}")
            print(f"[KeyBear] Found legacy 一二形象/键盘.png: {LEGACY_YIER_KEYBOARD_PATH.exists()}")
            print(f"[KeyBear] Keyboard style: {self.settings.get('keyboard_style')}")
            theme_name, palette = self._theme_palette()
            print(f"[KeyBear] keyboard_theme: {theme_name}")
            print(f"[KeyBear] normal_key_fill: {palette['normal_fill']}")
            print(f"[KeyBear] special_key_fill: {palette['special_fill']}")
            print(f"[KeyBear] Keyboard source image: {YIER_KEYBOARD_PATH if YIER_KEYBOARD_PATH.exists() else None}")
            print(f"[KeyBear] Loaded keyboard image: {loaded}")
            print(f"[KeyBear] Generated keyboard drawing: {self.using_fallback}")
            print(f"[KeyBear] Using keyboard cache: {'yes' if self.keyboard_image_path == PROCESSED_KEYBOARD_PATH else 'no'}")
            print(f"[KeyBear] Keyboard cache path: {PROCESSED_KEYBOARD_PATH if PROCESSED_KEYBOARD_PATH.exists() else None}")
            print(f"[KeyBear] active_keys at startup: {sorted(self.pressed)}")
            print(f"[KeyBear] bear_y_offset: {self.settings.get('bear_y_offset')}")
            print(f"[KeyBear] keyboard_scale: {self.settings.get('keyboard_scale')}")

        def set_key_down(self, label):
            if self.layout_model.key_spec(label) is not None:
                self.pressed.add(label)
                self.update()

        def set_key_up(self, label):
            self.pressed.discard(label)
            self.update()

        def all_key_labels(self):
            return self.layout_model.labels

        def key_side(self, label, middle_default="right"):
            side = self.layout_model.key_side(label)
            return middle_default if side == "middle" else side

        def _rect_for_key(self, key):
            return QRectF(
                key.x * self.width(),
                key.y * self.height(),
                key.w * self.width(),
                key.h * self.height(),
            )

        def _theme_palette(self):
            if KEY_TYPE_DEBUG:
                return "debug_key_types", KEYBOARD_THEMES["debug_key_types"]
            theme = self.settings.get("keyboard_theme", "light_keycaps")
            if theme not in KEYBOARD_THEMES or theme == "debug_key_types":
                theme = "light_keycaps"
            return theme, KEYBOARD_THEMES[theme]

        @staticmethod
        def _color(value, alpha=None):
            color = QColor(value)
            if alpha is not None:
                color.setAlpha(alpha)
            return color

        def paintEvent(self, _event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            if self.settings.get("keyboard_style") == "图片键盘" and not self.keyboard_pixmap.isNull():
                painter.drawPixmap(QRect(0, 0, self.width(), self.height()), self.keyboard_pixmap)
            else:
                self._draw_generated_keyboard(painter)
            self._draw_highlights(painter)

        def _draw_highlights(self, painter):
            _theme, palette = self._theme_palette()
            if not self.pressed:
                return
            painter.setPen(Qt.NoPen)
            for label in self.pressed:
                key = self.layout_model.key_spec(label)
                if key is None:
                    continue
                rect = self._rect_for_key(key).adjusted(2, 2, -2, -2)
                path = QPainterPath()
                radius = max(5, rect.height() * 0.22)
                path.addRoundedRect(rect, radius, radius)
                painter.fillPath(path, self._color(palette["pressed_fill"], palette["pressed_alpha"]))

        def _draw_generated_keyboard(self, painter):
            theme_name, palette = self._theme_palette()
            if not self._printed_generated_palette:
                print("[KeyBear] Drawing keycaps in: virtual_keyboard.py / VirtualKeyboard._draw_generated_keyboard")
                print(f"[KeyBear] keyboard_theme: {theme_name}")
                print(f"[KeyBear] key_type_debug: {KEY_TYPE_DEBUG}")
                print(f"[KeyBear] normal_key_fill: {palette['normal_fill']}")
                print(f"[KeyBear] special_key_fill: {palette['special_fill']}")
                print(f"[KeyBear] tray_fill: {palette['tray_fill']}")
                print(f"[KeyBear] key_border: {palette['border']} alpha={palette['border_alpha']}")
                print(f"[KeyBear] special_key_border: {palette['special_border']} alpha={palette['special_border_alpha']}")
                print(f"[KeyBear] text_color: {palette['text']}")
                print(f"[KeyBear] pressed_key_fill: {palette['pressed_fill']} alpha={palette['pressed_alpha']}")
                print(f"[KeyBear] keyboard_density: {self.settings.get('keyboard_density', 'clean')}")
                print(f"[KeyBear] keyboard_key_outline: {self.settings.get('keyboard_key_outline', KEY_OUTLINE_MODE)}")
                print(f"[KeyBear] hide_key_text: {HIDE_KEY_TEXT}")
                print(f"[KeyBear] hide_key_outline: {HIDE_KEY_OUTLINE}")
                print(f"[KeyBear] active_keys: {sorted(self.pressed)}")
            w = self.width()
            h = self.height()
            outer = QRectF(w * 0.025, h * 0.085, w * 0.95, h * 0.84)
            inner = QRectF(w * 0.06, h * 0.245, w * 0.88, h * 0.63)
            face_y = h * 0.18

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#5B321F"))
            painter.drawEllipse(QRectF(w * 0.23, h * 0.005, w * 0.105, h * 0.18))
            painter.drawEllipse(QRectF(w * 0.66, h * 0.005, w * 0.105, h * 0.18))

            outer_path = QPainterPath()
            outer_path.addRoundedRect(outer, h * 0.08, h * 0.08)
            painter.fillPath(outer_path, QColor("#5B321F"))

            body = outer.adjusted(w * 0.014, h * 0.028, -w * 0.014, -h * 0.028)
            body_path = QPainterPath()
            body_path.addRoundedRect(body, h * 0.07, h * 0.07)
            painter.fillPath(body_path, QColor("#FFF8E8"))

            tray_pen = self._color(palette["tray_pen"], palette["tray_pen_alpha"])
            painter.setPen(QPen(tray_pen, max(0.8, w * 0.0011)))
            painter.setBrush(QColor(palette["tray_fill"]))
            painter.drawRoundedRect(inner, h * 0.035, h * 0.035)
            if not self._printed_generated_palette:
                print("[KeyBear] key tray drawn: yes")
                print(f"[KeyBear] key_tray_fill: {palette['tray_fill']}")
                print(f"[KeyBear] key_tray_pen: {palette['tray_pen']} alpha={palette['tray_pen_alpha']}")
                print(f"[KeyBear] key_shadow: {palette['shadow']}")
                print(f"[KeyBear] painter_opacity: {painter.opacity()}")

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#F7B8B2"))
            painter.drawEllipse(QRectF(w * 0.385, face_y, w * 0.045, h * 0.052))
            painter.drawEllipse(QRectF(w * 0.570, face_y, w * 0.045, h * 0.052))
            painter.setBrush(QColor("#5B321F"))
            painter.drawEllipse(QRectF(w * 0.420, face_y - h * 0.026, w * 0.027, h * 0.050))
            painter.drawEllipse(QRectF(w * 0.553, face_y - h * 0.026, w * 0.027, h * 0.050))
            painter.setPen(QPen(QColor("#5B321F"), max(2, int(w * 0.006)), Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(QRectF(w * 0.484, face_y - h * 0.008, w * 0.018, h * 0.035), 200 * 16, 150 * 16)
            painter.drawArc(QRectF(w * 0.501, face_y - h * 0.008, w * 0.018, h * 0.035), 190 * 16, 150 * 16)

            key_rects = []
            for key in self.layout_model.keys:
                base_rect = self._rect_for_key(key)
                rect = base_rect.adjusted(0.4, 0.3, -0.4, -0.3)
                key_rects.append((key, rect))
                path = QPainterPath()
                radius = max(5, rect.height() * 0.24)
                path.addRoundedRect(rect, radius, radius)
                is_special = key.key_type == "special"
                fill_color = palette["special_fill"] if is_special else palette["normal_fill"]
                border_color = palette["special_border"] if is_special else palette["border"]
                border_alpha = palette["special_border_alpha"] if is_special else palette["border_alpha"]
                painter.fillPath(path, QColor(fill_color))
                outline_mode = self.settings.get("keyboard_key_outline", KEY_OUTLINE_MODE)
                if not HIDE_KEY_OUTLINE:
                    border = QColor(border_color)
                    alpha = border_alpha
                    if outline_mode != "minimal":
                        alpha = min(180, alpha + 35)
                    border.setAlpha(alpha)
                    pen_width = max(0.4, min(0.65, self.width() / 1400))
                    if outline_mode != "minimal":
                        pen_width = max(0.7, min(1.0, self.width() / 1000))
                    painter.setPen(QPen(border, pen_width))
                    painter.drawPath(path)
                if not self._printed_generated_palette and key.id in DEBUG_KEY_IDS:
                    print(
                        "[KeyBear] draw "
                        f"key_id={key.id}, label={key.label}, type={key.key_type}, "
                        f"is_special={is_special}, is_pressed={key.id in self.pressed}, "
                        f"fill_color={fill_color}, border_color={border_color} alpha={border_alpha}, "
                        f"text_color={palette['text']}, rect={rect}"
                    )

            if not self._printed_generated_palette and key_rects:
                sample_key, sample_rect = key_rects[0]
                sample_area = sample_rect.width() * sample_rect.height()
                outer_area = self.width() * self.height()
                print(f"[KeyBear] sample_key_fill_rect: {sample_key.label} {sample_rect}")
                print(f"[KeyBear] key_fill_area_to_widget_ratio: {sample_area / outer_area:.5f}")
                print(f"[KeyBear] key_outline_pen_width: {max(0.4, min(0.65, self.width() / 1400)):.2f}")
                print(f"[KeyBear] key_font_weight: regular")
                print("[KeyBear] overlay_after_keycaps: yes, only when active_keys is non-empty")
                self._printed_generated_palette = True

            if not HIDE_KEY_TEXT:
                font_size = max(7, int(self.height() * 0.029))
                font = QFont("Microsoft YaHei UI", font_size, QFont.Normal)
                font.setStyleStrategy(QFont.PreferAntialias)
                painter.setFont(font)
                painter.setPen(QColor(palette["text"]))
                painter.setBrush(Qt.NoBrush)
                for key, rect in key_rects:
                    painter.drawText(rect.adjusted(2, 0, -2, 0), Qt.AlignCenter, key.label)

except ImportError:
    VirtualKeyboard = None
