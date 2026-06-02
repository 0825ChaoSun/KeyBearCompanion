import json
from pathlib import Path

from path_utils import resource_path, user_data_path


DEFAULT_SETTINGS_PATH = resource_path("settings.json")
SETTINGS_PATH = user_data_path("settings.json")

SIZE_PRESETS = {
    "small": {"overall_scale": 0.70, "keyboard_scale": 0.55, "bear_scale": 0.75},
    "medium": {"overall_scale": 0.85, "keyboard_scale": 0.68, "bear_scale": 0.90},
    "large": {"overall_scale": 1.00, "keyboard_scale": 0.80, "bear_scale": 1.05},
}

SIZE_PRESET_LABELS = {
    "small": "小",
    "medium": "中",
    "large": "大",
}

KEYBOARD_LAYOUTS = {"qwerty", "main", "shortcut"}
KEYBOARD_LAYOUT_LABELS = {
    "qwerty": "简化 QWERTY",
    "main": "只显示主键区",
    "shortcut": "只显示快捷键区",
}

KEYBOARD_DENSITIES = {"clean", "full"}
KEYBOARD_KEY_OUTLINES = {"minimal", "normal"}

LIGHT_DEFAULTS = {
    "size_preset": "small",
    "overall_scale": 0.70,
    "bear_scale": 0.75,
    "cat_size": 229,
    "keyboard_scale": 0.55,
    "keyboard_style": "generated",
    "keyboard_theme": "light_keycaps",
    "keyboard_view_mode": "front",
    "use_transparent_processed": True,
    "use_keyboard_image": False,
    "scene_rotation_degrees": 0.0,
    "bear_y_offset": -70,
    "keyboard_overlap": 44,
    "sleep_bear_on_top": True,
    "keyboard_layout": "qwerty",
    "keyboard_density": "clean",
    "keyboard_key_outline": "minimal",
    "show_full_keyboard": True,
    "show_combo_hint": True,
    "key_sink_animation": False,
    "paw_sync_enabled": False,
    "breathing_animation": False,
    "key_bounce_animation": False,
    "sleep_animation": False,
    "cat_style": "yier_bear",
    "speech_bubble_enabled": False,
    "record_keys": False,
    "edge_snap_enabled": True,
    "edge_snap_margin": 24,
    "tray_enabled": True,
    "temporary_hide_minutes": 5,
}

FORCED_SIMPLIFIED_SETTINGS = {
    "keyboard_style": "generated",
    "keyboard_theme": "light_keycaps",
    "keyboard_view_mode": "front",
    "use_transparent_processed": True,
    "use_keyboard_image": False,
    "scene_rotation_degrees": 0.0,
    "show_combo_hint": True,
    "key_sink_animation": False,
    "paw_sync_enabled": False,
    "breathing_animation": False,
    "key_bounce_animation": False,
    "sleep_animation": False,
    "cat_style": "yier_bear",
    "speech_bubble_enabled": False,
    "record_keys": False,
}

DEFAULT_SETTINGS = {
    "always_on_top": True,
    "window_opacity": 1.0,
    "show_cat": True,
    "show_keyboard": True,
    "key_highlight_ms": 170,
    "idle_expression_shuffle": True,
    "idle_expression_min_seconds": 3,
    "idle_expression_max_seconds": 7,
    "sleep_wait_seconds": 180,
    "special_key_wow": True,
    "backspace_sad": True,
    "blink_enabled": False,
    "sleep_enabled": True,
    "fast_typing_reaction": True,
    "start_on_boot": False,
    "keyboard_debug": False,
    "window_x": None,
    "window_y": None,
    "light_defaults_version": 1,
    **LIGHT_DEFAULTS,
}

LEGACY_SIZE = {
    "灏?": "small",
    "小": "small",
    "涓?": "medium",
    "中": "medium",
    "澶?": "large",
    "大": "large",
}

LEGACY_LAYOUT = {
    "绠€鍖?QWERTY": "qwerty",
    "简化 QWERTY": "qwerty",
    "鍙樉绀轰富閿尯": "main",
    "只显示主键区": "main",
    "鍙樉绀哄揩鎹烽敭鍖?": "shortcut",
    "只显示快捷键区": "shortcut",
}


class SettingsManager:
    """Load and persist KeyBear settings. Key logging is never enabled."""

    def __init__(self, path=None):
        self.use_default_resource = path is None
        self.path = Path(path) if path is not None else SETTINGS_PATH
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.use_default_resource and DEFAULT_SETTINGS_PATH.exists():
            self._merge_known(self._read_json(DEFAULT_SETTINGS_PATH))
        if self.path.exists():
            self._merge_known(self._read_json(self.path))
        self._normalize()
        self.save()
        print(f"[KeyBear] Default settings resource: {DEFAULT_SETTINGS_PATH}")
        print(f"[KeyBear] User settings path: {self.path}")
        return self.settings

    def _read_json(self, path):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def _merge_known(self, data):
        if isinstance(data, dict):
            self.settings.update({key: data[key] for key in DEFAULT_SETTINGS if key in data})

    def apply_size_preset(self, preset):
        preset = LEGACY_SIZE.get(preset, preset)
        preset = preset if preset in SIZE_PRESETS else "small"
        self.settings["size_preset"] = preset
        self.settings.update(SIZE_PRESETS[preset])

    def _normalize(self):
        self.settings["size_preset"] = LEGACY_SIZE.get(self.settings.get("size_preset"), self.settings.get("size_preset"))
        if self.settings.get("size_preset") not in SIZE_PRESETS:
            self.settings["size_preset"] = "small"

        self.settings["keyboard_layout"] = LEGACY_LAYOUT.get(
            self.settings.get("keyboard_layout"),
            self.settings.get("keyboard_layout"),
        )
        if self.settings.get("keyboard_layout") not in KEYBOARD_LAYOUTS:
            self.settings["keyboard_layout"] = "qwerty"
        if self.settings.get("keyboard_density") not in KEYBOARD_DENSITIES:
            self.settings["keyboard_density"] = "clean"
        if self.settings.get("keyboard_key_outline") not in KEYBOARD_KEY_OUTLINES:
            self.settings["keyboard_key_outline"] = "minimal"

        # Migrate stale debug-era settings to the lightweight default layout
        # once. Afterwards user-facing size/position settings remain editable.
        if self.settings.get("light_defaults_version") != 1:
            self.settings.update(LIGHT_DEFAULTS)
            self.settings["light_defaults_version"] = 1

        # Removed options stay fixed so old config cannot re-enable buggy paths.
        self.settings.update(FORCED_SIMPLIFIED_SETTINGS)

        self.settings["window_opacity"] = 1.0
        self.settings["key_highlight_ms"] = int(min(1000, max(40, self.settings.get("key_highlight_ms", 170))))
        self.settings["sleep_wait_seconds"] = int(min(3600, max(20, self.settings.get("sleep_wait_seconds", 180))))
        self.settings["edge_snap_margin"] = int(min(96, max(0, self.settings.get("edge_snap_margin", 24))))
        self.settings["temporary_hide_minutes"] = int(
            min(60, max(1, self.settings.get("temporary_hide_minutes", 5)))
        )
        for key in ("window_x", "window_y"):
            value = self.settings.get(key)
            self.settings[key] = int(value) if isinstance(value, (int, float)) else None
        self.settings["idle_expression_min_seconds"] = int(
            min(20, max(2, self.settings.get("idle_expression_min_seconds", 3)))
        )
        self.settings["idle_expression_max_seconds"] = int(
            min(30, max(self.settings["idle_expression_min_seconds"], self.settings.get("idle_expression_max_seconds", 7)))
        )

    def save(self):
        self._normalize()
        self.path.write_text(json.dumps(self.settings, ensure_ascii=False, indent=2), encoding="utf-8")

    def get(self, key, default=None):
        fallback = DEFAULT_SETTINGS.get(key, default)
        return self.settings.get(key, fallback)

    def update(self, values):
        self.settings.update(values)
        if "size_preset" in values:
            self.apply_size_preset(values["size_preset"])
        self.save()
