SPECIAL_KEYS = {
    "ctrl_l": "LeftCtrl",
    "ctrl_r": "RightCtrl",
    "ctrl": "LeftCtrl",
    "shift_l": "LeftShift",
    "shift_r": "RightShift",
    "shift": "LeftShift",
    "alt_l": "LeftAlt",
    "alt_r": "RightAlt",
    "alt": "LeftAlt",
    "cmd": "Win",
    "cmd_l": "Win",
    "cmd_r": "Win",
    "space": "Space",
    "backspace": "Backspace",
    "enter": "Enter",
    "tab": "Tab",
    "esc": "Esc",
    "caps_lock": "Caps",
}


def normalize_key_name(key):
    """Map pynput keys/chars to virtual-keyboard labels without storing content."""

    raw = str(key)
    if raw.startswith("Key."):
        raw = raw[4:]
    if raw.startswith("'") and raw.endswith("'") and len(raw) >= 3:
        raw = raw[1:-1]
    raw = raw.lower()
    if raw in SPECIAL_KEYS:
        return SPECIAL_KEYS[raw]
    if len(raw) == 1 and raw.isalnum():
        return raw.upper()
    return None


class KeyboardListener:
    """Thin pynput adapter. It forwards realtime key names and keeps no logs."""

    def __init__(self, on_press, on_release, debug=False):
        self.on_press = on_press
        self.on_release = on_release
        self.debug = debug
        self.listener = None

    def start(self):
        from pynput import keyboard

        self.listener = keyboard.Listener(on_press=self._press, on_release=self._release)
        self.listener.daemon = True
        self.listener.start()

    def stop(self):
        if self.listener is not None:
            self.listener.stop()
            self.listener = None

    def _press(self, key):
        name = normalize_key_name(getattr(key, "char", None) or key)
        if name:
            if self.debug:
                print(f"[KeyBear] key down: {name}")
            self.on_press(name)

    def _release(self, key):
        name = normalize_key_name(getattr(key, "char", None) or key)
        if name:
            if self.debug:
                print(f"[KeyBear] key up: {name}")
            self.on_release(name)
