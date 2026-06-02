from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from settings_manager import KEYBOARD_LAYOUT_LABELS, SIZE_PRESET_LABELS, SIZE_PRESETS


QSS = """
QDialog {
    background: #FFF8E8;
    color: #3B2A22;
    font-family: "Microsoft YaHei UI";
    font-size: 10.5pt;
}
QScrollArea { border: none; background: transparent; }
QFrame#card {
    background: #FFFFFF;
    border: 1px solid #F0D6B3;
    border-radius: 16px;
}
QLabel#title { font-size: 20px; font-weight: 700; }
QLabel#section {
    color: #8B623E;
    font-size: 12pt;
    font-weight: 700;
    margin-top: 14px;
}
QLabel#hint { color: #8B623E; }
QSpinBox, QDoubleSpinBox, QComboBox {
    background: #FFF8E8;
    border: 1px solid #E3C39A;
    border-radius: 8px;
    min-height: 30px;
    padding: 4px 8px;
}
QPushButton#saveButton {
    background: #E89F5A;
    color: white;
    border: none;
    border-radius: 11px;
    min-height: 38px;
    padding: 8px 18px;
    font-weight: 700;
}
"""


class SettingsWindow(QDialog):
    saved = Signal()

    def __init__(self, settings, startup_manager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.startup_manager = startup_manager
        self.setWindowTitle("KeyBear Companion 设置")
        self.resize(840, 700)
        self.setMinimumSize(840, 560)
        self.setStyleSheet(QSS)
        self._build()
        self._load()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, 1)

        card = QFrame()
        card.setObjectName("card")
        scroll.setWidget(card)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(10)

        title = QLabel("KeyBear Companion")
        title.setObjectName("title")
        layout.addWidget(title)

        self.always_on_top = QCheckBox("窗口置顶")
        self.size_preset = QComboBox()
        for value, label in SIZE_PRESET_LABELS.items():
            self.size_preset.addItem(label, value)
        self.overall_scale = self._double_spin(0.60, 1.15, 0.05)
        self.cat_size = self._spin(120, 320)
        self.bear_scale = self._double_spin(0.65, 1.15, 0.05)
        self.bear_y_offset = self._spin(-180, 100)
        self.keyboard_scale = self._double_spin(0.45, 0.95, 0.05)
        self.size_preset.currentIndexChanged.connect(self._apply_size_preset_to_controls)
        self.show_cat = QCheckBox("显示小熊")
        self.show_keyboard = QCheckBox("显示键盘")
        self.edge_snap = QCheckBox("启用贴边吸附")
        self.edge_snap_margin = self._spin(0, 96)
        self.tray_enabled = QCheckBox("启用系统托盘图标")
        self.temporary_hide_minutes = self._spin(1, 60)

        self.keyboard_layout = QComboBox()
        for value, label in KEYBOARD_LAYOUT_LABELS.items():
            self.keyboard_layout.addItem(label, value)
        self.keyboard_density = QComboBox()
        self.keyboard_density.addItems(["clean", "full"])
        self.keyboard_outline = QComboBox()
        self.keyboard_outline.addItems(["minimal", "normal"])
        self.highlight_ms = self._spin(40, 1000)
        self.keyboard_debug = QCheckBox("终端打印按键映射调试日志")

        self.idle_shuffle = QCheckBox("待机时随机切换站立 / 微笑 / 开心")
        self.idle_min = self._spin(2, 20)
        self.idle_max = self._spin(3, 30)
        self.sleep_enabled = QCheckBox("启用睡眠状态")
        self.sleep_wait = self._spin(20, 3600)
        self.sleep_on_top = QCheckBox("睡眠时小熊趴在键盘上方")
        self.special_wow = QCheckBox("特殊键触发 wow 表情")
        self.backspace_sad = QCheckBox("Backspace 触发伤心表情")
        self.fast = QCheckBox("启用快速输入反应")
        self.start_on_boot = QCheckBox("开机启动，默认关闭")

        self._section(
            layout,
            "基础设置",
            [
                self._row("界面大小", self.size_preset),
                self.always_on_top,
                self._row("整体缩放比例", self.overall_scale),
                self._row("小熊基础大小", self.cat_size),
                self._row("小熊缩放比例", self.bear_scale),
                self._row("小熊上下偏移", self.bear_y_offset),
                self._row("键盘缩放比例", self.keyboard_scale),
                self.show_cat,
                self.show_keyboard,
                self.edge_snap,
                self._row("贴边吸附距离 px", self.edge_snap_margin),
                self.tray_enabled,
                self._row("临时隐藏时间 min", self.temporary_hide_minutes),
            ],
        )
        self._section(
            layout,
            "键盘设置",
            [
                self._row("键盘布局", self.keyboard_layout),
                self._row("键盘密度", self.keyboard_density),
                self._row("键帽描边", self.keyboard_outline),
                self._row("高亮持续时间 ms", self.highlight_ms),
                self.keyboard_debug,
            ],
        )
        self._section(
            layout,
            "小熊状态",
            [
                self.idle_shuffle,
                self._row("待机最短间隔 s", self.idle_min),
                self._row("待机最长间隔 s", self.idle_max),
                self.sleep_enabled,
                self._row("睡眠等待时间 s", self.sleep_wait),
                self.sleep_on_top,
                self.special_wow,
                self.backspace_sad,
                self.fast,
            ],
        )
        self._section(layout, "启动设置", [self.start_on_boot])

        self.hint = QLabel("隐私：本软件只做实时动画同步，不保存、不上传、不记录任何按键内容。")
        self.hint.setObjectName("hint")
        self.hint.setWordWrap(True)
        layout.addWidget(self.hint)

        save = QPushButton("保存设置")
        save.setObjectName("saveButton")
        save.clicked.connect(self.save)
        outer.addWidget(save, 0, Qt.AlignRight)

    def _spin(self, low, high):
        spin = QSpinBox()
        spin.setRange(low, high)
        spin.setFixedWidth(320)
        return spin

    def _double_spin(self, low, high, step):
        spin = QDoubleSpinBox()
        spin.setRange(low, high)
        spin.setSingleStep(step)
        spin.setDecimals(2)
        spin.setFixedWidth(320)
        return spin

    def _section(self, layout, title, widgets):
        label = QLabel(title)
        label.setObjectName("section")
        layout.addWidget(label)
        for widget in widgets:
            layout.addWidget(widget)

    def _row(self, label, widget):
        row = QWidget()
        grid = QGridLayout(row)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(18)
        text = QLabel(label)
        text.setFixedWidth(250)
        widget.setMinimumWidth(320)
        grid.addWidget(text, 0, 0)
        grid.addWidget(widget, 0, 1)
        grid.setColumnStretch(1, 1)
        return row

    @staticmethod
    def _set_combo_data(combo, value):
        index = combo.findData(value)
        combo.setCurrentIndex(index if index >= 0 else 0)

    def _apply_size_preset_to_controls(self):
        preset = self.size_preset.currentData()
        values = SIZE_PRESETS.get(preset)
        if not values:
            return
        self.overall_scale.setValue(values["overall_scale"])
        self.keyboard_scale.setValue(values["keyboard_scale"])
        self.bear_scale.setValue(values["bear_scale"])

    def _load(self):
        self.always_on_top.setChecked(self.settings.get("always_on_top"))
        self.size_preset.blockSignals(True)
        self._set_combo_data(self.size_preset, self.settings.get("size_preset"))
        self.size_preset.blockSignals(False)
        self.overall_scale.setValue(self.settings.get("overall_scale"))
        self.cat_size.setValue(self.settings.get("cat_size"))
        self.bear_scale.setValue(self.settings.get("bear_scale"))
        self.bear_y_offset.setValue(self.settings.get("bear_y_offset"))
        self.keyboard_scale.setValue(self.settings.get("keyboard_scale"))
        self.show_cat.setChecked(self.settings.get("show_cat"))
        self.show_keyboard.setChecked(self.settings.get("show_keyboard"))
        self.edge_snap.setChecked(self.settings.get("edge_snap_enabled"))
        self.edge_snap_margin.setValue(self.settings.get("edge_snap_margin"))
        self.tray_enabled.setChecked(self.settings.get("tray_enabled"))
        self.temporary_hide_minutes.setValue(self.settings.get("temporary_hide_minutes"))
        self._set_combo_data(self.keyboard_layout, self.settings.get("keyboard_layout"))
        self.keyboard_density.setCurrentText(self.settings.get("keyboard_density", "clean"))
        self.keyboard_outline.setCurrentText(self.settings.get("keyboard_key_outline", "minimal"))
        self.highlight_ms.setValue(self.settings.get("key_highlight_ms"))
        self.keyboard_debug.setChecked(self.settings.get("keyboard_debug"))
        self.idle_shuffle.setChecked(self.settings.get("idle_expression_shuffle"))
        self.idle_min.setValue(self.settings.get("idle_expression_min_seconds"))
        self.idle_max.setValue(self.settings.get("idle_expression_max_seconds"))
        self.sleep_enabled.setChecked(self.settings.get("sleep_enabled"))
        self.sleep_wait.setValue(self.settings.get("sleep_wait_seconds"))
        self.sleep_on_top.setChecked(self.settings.get("sleep_bear_on_top"))
        self.special_wow.setChecked(self.settings.get("special_key_wow"))
        self.backspace_sad.setChecked(self.settings.get("backspace_sad"))
        self.fast.setChecked(self.settings.get("fast_typing_reaction"))
        self.start_on_boot.setChecked(self.settings.get("start_on_boot"))

    def save(self):
        values = {
            "always_on_top": self.always_on_top.isChecked(),
            "size_preset": self.size_preset.currentData(),
            "overall_scale": self.overall_scale.value(),
            "cat_size": self.cat_size.value(),
            "bear_scale": self.bear_scale.value(),
            "bear_y_offset": self.bear_y_offset.value(),
            "keyboard_scale": self.keyboard_scale.value(),
            "show_cat": self.show_cat.isChecked(),
            "show_keyboard": self.show_keyboard.isChecked(),
            "edge_snap_enabled": self.edge_snap.isChecked(),
            "edge_snap_margin": self.edge_snap_margin.value(),
            "tray_enabled": self.tray_enabled.isChecked(),
            "temporary_hide_minutes": self.temporary_hide_minutes.value(),
            "keyboard_layout": self.keyboard_layout.currentData(),
            "keyboard_density": self.keyboard_density.currentText(),
            "keyboard_key_outline": self.keyboard_outline.currentText(),
            "key_highlight_ms": self.highlight_ms.value(),
            "keyboard_debug": self.keyboard_debug.isChecked(),
            "idle_expression_shuffle": self.idle_shuffle.isChecked(),
            "idle_expression_min_seconds": self.idle_min.value(),
            "idle_expression_max_seconds": self.idle_max.value(),
            "sleep_enabled": self.sleep_enabled.isChecked(),
            "sleep_wait_seconds": self.sleep_wait.value(),
            "sleep_bear_on_top": self.sleep_on_top.isChecked(),
            "special_key_wow": self.special_wow.isChecked(),
            "backspace_sad": self.backspace_sad.isChecked(),
            "fast_typing_reaction": self.fast.isChecked(),
            "start_on_boot": self.start_on_boot.isChecked(),
        }
        ok, message = self.startup_manager.set_enabled(values["start_on_boot"])
        if not ok:
            values["start_on_boot"] = False
            self.start_on_boot.setChecked(False)
        self.settings.update(values)
        self._load()
        self.hint.setText(message if values["start_on_boot"] or not ok else "设置已保存。隐私：不会保存任何按键内容。")
        self.saved.emit()
