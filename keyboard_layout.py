from dataclasses import dataclass


@dataclass(frozen=True)
class KeySpec:
    id: str
    label: str
    key_type: str
    x: float
    y: float
    w: float
    h: float

    @property
    def points(self):
        return (
            (self.x, self.y),
            (self.x + self.w, self.y),
            (self.x + self.w, self.y + self.h),
            (self.x, self.y + self.h),
        )

    def center(self):
        return self.x + self.w / 2, self.y + self.h / 2


FULL_ROWS = [
    ["Esc", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Backspace"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", "Enter"],
    ["LeftShift", "Z", "X", "C", "V", "B", "N", "M", "RightShift"],
    ["LeftCtrl", "Win", "LeftAlt", "Space", "RightAlt", "RightCtrl"],
]

CLEAN_ROWS = [
    ["Esc", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Backspace"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", "Enter"],
    ["LeftShift", "Z", "X", "C", "V", "B", "N", "M", "RightShift"],
    ["LeftCtrl", "LeftAlt", "Space", "RightAlt", "RightCtrl"],
]

WIDTHS = {
    "Esc": 1.15,
    "Backspace": 2.05,
    "Tab": 1.55,
    "Caps": 1.85,
    "Enter": 2.10,
    "LeftShift": 2.25,
    "RightShift": 2.25,
    "LeftCtrl": 1.35,
    "RightCtrl": 1.75,
    "Win": 1.25,
    "LeftAlt": 1.35,
    "RightAlt": 1.35,
    "Space": 5.35,
}

ALIASES = {
    "Shift": "LeftShift",
    "Ctrl": "LeftCtrl",
    "Alt": "LeftAlt",
}

DISPLAY_LABELS = {
    "LeftShift": "Shift",
    "RightShift": "Shift",
    "LeftCtrl": "Ctrl",
    "RightCtrl": "Ctrl",
    "LeftAlt": "Alt",
    "RightAlt": "Alt",
    "Backspace": "Back",
}


def key_type_for(key_id):
    return "normal" if len(key_id) == 1 and key_id.isalnum() else "special"


class KeyboardLayout:
    """Stable normalized hit zones for generated/image keyboard surfaces."""

    def __init__(self, variant="简化 QWERTY", density="clean"):
        self.variant = variant
        self.density = density
        self.keys = self._build()
        self._by_id = {key.id: key for key in self.keys}

    def _base_rows(self):
        return CLEAN_ROWS if self.density == "clean" else FULL_ROWS

    def _active_rows(self):
        rows = self._base_rows()
        if self.variant in {"只显示快捷键区", "shortcut"}:
            return [["LeftCtrl", "C", "V", "S", "LeftAlt", "Tab", "Enter"]]
        if self.variant in {"只显示主键区", "main"}:
            return rows[1:4]
        return rows

    def _build(self):
        rows = self._active_rows()
        row_tops = [0.285, 0.403, 0.522, 0.641, 0.761]
        row_h = 0.100
        row_left = 0.055
        row_width = 0.865
        key_gap_units = 0.18 if self.density == "clean" else 0.10
        specs = []

        for row_index, row in enumerate(rows):
            units = sum(WIDTHS.get(label, 1.0) for label in row)
            units += key_gap_units * (len(row) - 1)
            unit = row_width / units
            x = row_left
            y = row_tops[min(row_index, len(row_tops) - 1)]
            for key_id in row:
                w = WIDTHS.get(key_id, 1.0) * unit
                specs.append(
                    KeySpec(
                        id=key_id,
                        label=DISPLAY_LABELS.get(key_id, key_id),
                        key_type=key_type_for(key_id),
                        x=x,
                        y=y,
                        w=w,
                        h=row_h,
                    )
                )
                x += w + key_gap_units * unit
        return specs

    @property
    def labels(self):
        return [key.id for key in self.keys]

    def key_spec(self, label):
        return self._by_id.get(ALIASES.get(label, label))

    def key_center(self, label):
        spec = self.key_spec(label)
        return spec.center() if spec else None

    def key_side(self, label):
        center = self.key_center(label)
        if center is None:
            return "middle"
        if center[0] < 0.47:
            return "left"
        if center[0] > 0.53:
            return "right"
        return "middle"
