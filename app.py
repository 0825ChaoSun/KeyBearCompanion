import sys
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from animation_controller import AnimationController
from idle_detector import IdleDetector
from keyboard_listener import KeyboardListener
from path_utils import resource_path
from pet_keyboard_window import PetKeyboardWindow
from settings_manager import SettingsManager
from settings_window import SettingsWindow
from startup_manager import StartupManager


def _prepare_source_assets(settings):
    """Prepare editable source-mode assets without pulling Pillow into frozen builds."""
    if getattr(sys, "frozen", False):
        return
    try:
        if settings.get("use_transparent_processed"):
            from transparent_processor import process_assets

            process_assets(overwrite=False)
        from asset_generator import ASSETS_DIR, generate_assets

        generate_assets(ASSETS_DIR, overwrite=False)
    except Exception as exc:
        print(f"[KeyBear] source asset preparation skipped: {exc}")


class KeyCatCompanion:
    """Qt application coordinator. Key events are only used for realtime animation."""

    def __init__(self, test_keys=False):
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setQuitOnLastWindowClosed(False)
        self.qt_app.setApplicationName("KeyBear Companion")
        self.settings = SettingsManager()
        _prepare_source_assets(self.settings)
        self.window = PetKeyboardWindow(self.settings)
        self.tray_icon = None
        self.tray_menu = None
        self.temporary_hide_timer = QTimer(self.qt_app)
        self.temporary_hide_timer.setSingleShot(True)
        self.temporary_hide_timer.timeout.connect(self.restore_window)
        self.idle_detector = IdleDetector()
        self.animation = AnimationController(self.window, self.settings, self.idle_detector)
        self.startup = StartupManager()
        self.settings_window = SettingsWindow(self.settings, self.startup, self.window)
        self.listener = KeyboardListener(
            self.handle_key_press,
            self.handle_key_release,
            debug=self.settings.get("keyboard_debug") or test_keys,
        )
        self.recent_presses = []
        self.last_middle_side = "left"
        self._connect()
        self._setup_tray()
        if not test_keys:
            self.animation.start()
            self.listener.start()
        self.window.show()
        if test_keys:
            QTimer.singleShot(500, self.run_key_highlight_test)

    def _connect(self):
        self.window.request_settings.connect(self.open_settings)
        self.window.request_toggle_layout.connect(self.toggle_layout)
        self.window.request_toggle_cat.connect(self.toggle_cat)
        self.window.request_toggle_keyboard.connect(self.toggle_keyboard)
        self.window.request_temporary_hide.connect(self.temporary_hide)
        self.window.request_quit.connect(self.quit)
        self.settings_window.saved.connect(self.apply_settings)
        self.qt_app.aboutToQuit.connect(self.window.save_window_position)
        self.qt_app.aboutToQuit.connect(self.listener.stop)

    def run(self):
        return self.qt_app.exec()

    def handle_key_press(self, label):
        self.animation.mark_input()
        self.window.keyboard.set_key_down(label)
        now = time.monotonic()
        self.recent_presses = [stamp for stamp in self.recent_presses if now - stamp < 1.2]
        self.recent_presses.append(now)
        pressed = self.window.keyboard.pressed

        if label == "Backspace" and self.settings.get("backspace_sad"):
            self.animation.set_overlay("sad", 1100)
            return
        if label in {"S", "C", "V"} and self._ctrl_is_down(pressed):
            self.animation.set_overlay("happy", 1000)
            return
        if not self._is_plain_letter_or_digit(label):
            if self.settings.get("special_key_wow"):
                self.animation.set_overlay("wow", 850)
            return

        side = self.window.keyboard.key_side(label, self.last_middle_side)
        self.last_middle_side = side
        self.animation.press(side)
        if self.settings.get("fast_typing_reaction") and len(self.recent_presses) >= 8:
            self.animation.trigger_fast_typing()

    def handle_key_release(self, label):
        self.window.keyboard.set_key_up(label)
        side = self.window.keyboard.key_side(label, self.last_middle_side)
        self.animation.release(side)
        QTimer.singleShot(self.settings.get("key_highlight_ms"), self.window.keyboard.update)

    def _is_plain_letter_or_digit(self, label):
        return len(label) == 1 and label.isalnum()

    def _ctrl_is_down(self, pressed):
        return "LeftCtrl" in pressed or "RightCtrl" in pressed

    def run_key_highlight_test(self):
        labels = self.window.keyboard.all_key_labels()
        interval = 300

        def step(index):
            self.window.keyboard.pressed.clear()
            if index >= len(labels):
                self.window.keyboard.update()
                print("[KeyBear] key highlight test finished")
                return
            label = labels[index]
            print(f"[KeyBear] testing key: {label}")
            self.window.keyboard.set_key_down(label)
            QTimer.singleShot(interval, lambda: step(index + 1))

        step(0)

    def open_settings(self):
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def apply_settings(self):
        self.window.apply_settings()
        self._setup_tray()

    def _app_icon(self):
        for relative in ("assets/processed/app_icon.ico", "assets/processed/app_icon.png"):
            path = resource_path(relative)
            if path.exists():
                return QIcon(str(path))
        return QIcon()

    def _setup_tray(self):
        if not self.settings.get("tray_enabled"):
            if self.tray_icon:
                self.tray_icon.hide()
                self.tray_icon = None
                self.tray_menu = None
            return
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("[KeyBear] system tray is unavailable")
            return
        if self.tray_icon:
            self.tray_icon.hide()

        menu = QMenu()
        show_action = QAction("显示/隐藏", menu)
        show_action.triggered.connect(self.toggle_window_visible)
        hide_action = QAction("临时隐藏", menu)
        hide_action.triggered.connect(self.temporary_hide)
        settings_action = QAction("设置", menu)
        settings_action.triggered.connect(self.open_settings)
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.quit)
        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addSeparator()
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        self.tray_icon = QSystemTrayIcon(self._app_icon(), self.qt_app)
        self.tray_menu = menu
        self.tray_icon.setToolTip("KeyBear Companion")
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self._tray_activated)
        self.tray_icon.show()
        print("[KeyBear] tray icon enabled")

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_window_visible()

    def toggle_window_visible(self):
        if self.window.isVisible():
            self.window.save_window_position()
            self.window.hide()
        else:
            self.restore_window()

    def temporary_hide(self):
        self.window.save_window_position()
        self.window.hide()
        minutes = int(self.settings.get("temporary_hide_minutes", 5))
        self.temporary_hide_timer.start(minutes * 60 * 1000)
        print(f"[KeyBear] temporary hide for {minutes} minute(s)")

    def restore_window(self):
        self.temporary_hide_timer.stop()
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def toggle_layout(self):
        layouts = ["qwerty", "main", "shortcut"]
        current = layouts.index(self.settings.get("keyboard_layout"))
        self.settings.update({"keyboard_layout": layouts[(current + 1) % len(layouts)]})
        self.window.apply_settings()

    def toggle_cat(self):
        self.settings.update({"show_cat": not self.settings.get("show_cat")})
        self.window.apply_settings()

    def toggle_keyboard(self):
        self.settings.update({"show_keyboard": not self.settings.get("show_keyboard")})
        self.window.apply_settings()

    def quit(self):
        self.window.save_window_position()
        if self.tray_icon:
            self.tray_icon.hide()
        self.listener.stop()
        self.qt_app.quit()


def run():
    return KeyCatCompanion(test_keys="--test-keys" in sys.argv).run()
