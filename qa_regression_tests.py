import tempfile
import unittest
from pathlib import Path

from PySide6.QtCore import QPoint, QRect

from keyboard_layout import KeyboardLayout
from keyboard_listener import normalize_key_name
from pet_keyboard_window import clamp_window_position, snap_window_position
from settings_manager import SIZE_PRESETS, SettingsManager


class QinliangRegressionTests(unittest.TestCase):
    def test_settings_falls_back_when_preferred_path_is_unwritable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bad_settings_path = root / "settings.json"
            bad_settings_path.mkdir()
            fallback_path = root / "fallback" / "settings.json"

            manager = SettingsManager(path=bad_settings_path, fallback_path=fallback_path)

            self.assertEqual(manager.path, fallback_path)
            self.assertTrue(fallback_path.exists())
            self.assertTrue(manager.get("tray_enabled"))

    def test_explicit_scale_values_are_not_overwritten_by_size_preset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SettingsManager(Path(temp_dir) / "settings.json")

            manager.update(
                {
                    "size_preset": "small",
                    "overall_scale": 1.0,
                    "keyboard_scale": 0.95,
                    "bear_scale": 1.15,
                }
            )

            self.assertEqual(manager.get("size_preset"), "small")
            self.assertEqual(manager.get("overall_scale"), 1.0)
            self.assertEqual(manager.get("keyboard_scale"), 0.95)
            self.assertEqual(manager.get("bear_scale"), 1.15)

    def test_size_preset_only_update_still_applies_preset_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SettingsManager(Path(temp_dir) / "settings.json")

            manager.update({"size_preset": "large"})

            self.assertEqual(manager.get("overall_scale"), SIZE_PRESETS["large"]["overall_scale"])
            self.assertEqual(manager.get("keyboard_scale"), SIZE_PRESETS["large"]["keyboard_scale"])
            self.assertEqual(manager.get("bear_scale"), SIZE_PRESETS["large"]["bear_scale"])

    def test_keyboard_mapping_and_hotzones_cover_common_keys(self):
        layout = KeyboardLayout("qwerty", "clean")
        required = [
            "Esc",
            "Backspace",
            "Tab",
            "Caps",
            "Enter",
            "LeftShift",
            "RightShift",
            "LeftCtrl",
            "RightCtrl",
            "LeftAlt",
            "RightAlt",
            "Space",
            "Q",
            "A",
            "Z",
        ]
        self.assertEqual([key for key in required if layout.key_spec(key) is None], [])
        self.assertLess(layout.key_center("LeftShift")[0], layout.key_center("RightShift")[0])
        self.assertEqual(normalize_key_name("Key.backspace"), "Backspace")
        self.assertEqual(normalize_key_name("Key.shift_r"), "RightShift")
        self.assertEqual(normalize_key_name("'a'"), "A")

    def test_drag_bounds_allow_crossing_between_two_monitors(self):
        virtual_desktop = QRect(0, 0, 3840, 1080)

        point_on_second_monitor = clamp_window_position(QPoint(2100, 100), 320, 240, virtual_desktop)
        snapped_inside_second_monitor = snap_window_position(
            QPoint(2100, 100),
            320,
            240,
            virtual_desktop,
            margin=24,
            enabled=True,
        )

        self.assertEqual(point_on_second_monitor.x(), 2100)
        self.assertEqual(snapped_inside_second_monitor.x(), 2100)
        self.assertGreater(point_on_second_monitor.x(), 1920)


if __name__ == "__main__":
    unittest.main()
