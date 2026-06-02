from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import QApplication, QMenu, QWidget

from cat_widget import CatWidget
from virtual_keyboard import VirtualKeyboard


MENU_QSS = """
QMenu {
    background: #FFF6DF;
    color: #3B2A22;
    border: 1px solid #D8B98A;
    border-radius: 10px;
    padding: 8px;
    font-family: "Microsoft YaHei UI";
    font-size: 10pt;
}
QMenu::item {
    padding: 8px 26px;
    border-radius: 7px;
}
QMenu::item:selected {
    background: #F4D2A0;
}
"""


class PetKeyboardWindow(QWidget):
    request_settings = Signal()
    request_toggle_layout = Signal()
    request_toggle_cat = Signal()
    request_toggle_keyboard = Signal()
    request_temporary_hide = Signal()
    request_quit = Signal()

    def __init__(self, settings):
        super().__init__(None, Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.settings = settings
        self.is_dragging = False
        self.drag_offset = QPoint()
        self._base_cat_pos = QPoint()
        self._has_restored_position = False
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(settings.get("window_opacity"))
        self.cat = CatWidget(settings, self)
        self.keyboard = VirtualKeyboard(settings, self)
        self.apply_settings()
        self._restore_or_place()

    def apply_settings(self):
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.settings.get("always_on_top"):
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setWindowOpacity(self.settings.get("window_opacity"))
        self.cat.apply_settings()
        self.keyboard.apply_settings()
        self.cat.setVisible(self.settings.get("show_cat"))
        self.keyboard.setVisible(self.settings.get("show_keyboard"))
        self._layout_scene()
        if self._has_restored_position:
            self.move(self._clamp_point(self.pos()))
        self.show()

    def _layout_scene(self):
        cat_w = self.cat.width()
        cat_h = self.cat.height()
        key_w = self.keyboard.width()
        key_h = self.keyboard.height()
        overlap = int(self.settings.get("keyboard_overlap") * self.settings.get("overall_scale"))
        bear_y = int(self.settings.get("bear_y_offset") * self.settings.get("overall_scale"))
        margin = 24
        headroom = int(120 * self.settings.get("overall_scale"))
        width = max(cat_w, key_w) + margin * 2
        base_cat_y = margin + headroom
        keyboard_y = base_cat_y + cat_h - overlap
        height = keyboard_y + key_h + margin
        self.resize(width, height)

        cat_x = (width - cat_w) // 2
        cat_y = max(0, base_cat_y + bear_y)
        keyboard_x = (width - key_w) // 2
        self.cat.move(cat_x, cat_y)
        self._base_cat_pos = QPoint(cat_x, cat_y)
        self.keyboard.move(keyboard_x, keyboard_y)
        self.update_layering()

        print(f"[KeyBear] bear_y_offset: {self.settings.get('bear_y_offset')}")
        print(f"[KeyBear] keyboard_overlap: {self.settings.get('keyboard_overlap')}")
        print(f"[KeyBear] cat position: ({cat_x}, {cat_y})")
        print(f"[KeyBear] keyboard position: ({keyboard_x}, {keyboard_y})")

    def update_layering(self):
        if self.settings.get("sleep_bear_on_top") and self.cat.state == "sleep":
            self.keyboard.lower()
            sleep_y = self.keyboard.y() - int(self.cat.height() * 0.56)
            self.cat.move(self._base_cat_pos.x(), max(0, sleep_y))
            self.cat.raise_()
        else:
            self.cat.move(self._base_cat_pos)
            self.cat.lower()
            self.keyboard.raise_()

    def _available_geometry(self):
        screen = self.screen() or QApplication.primaryScreen()
        return screen.availableGeometry()

    def _place_bottom_right(self):
        screen = self._available_geometry()
        self.move(screen.right() - self.width() - 42, screen.bottom() - self.height() - 42)

    def _restore_or_place(self):
        x_pos = self.settings.get("window_x")
        y_pos = self.settings.get("window_y")
        if isinstance(x_pos, int) and isinstance(y_pos, int):
            self.move(self._clamp_point(QPoint(x_pos, y_pos)))
        else:
            self._place_bottom_right()
        self._has_restored_position = True
        print(f"[KeyBear] restored window position: ({self.x()}, {self.y()})")

    def _clamp_point(self, point):
        screen = self._available_geometry()
        max_x = max(screen.left(), screen.right() - self.width() + 1)
        max_y = max(screen.top(), screen.bottom() - self.height() + 1)
        return QPoint(min(max(point.x(), screen.left()), max_x), min(max(point.y(), screen.top()), max_y))

    def _snap_point(self, point):
        point = self._clamp_point(point)
        if not self.settings.get("edge_snap_enabled"):
            return point
        screen = self._available_geometry()
        margin = int(self.settings.get("edge_snap_margin", 24))
        x_pos = point.x()
        y_pos = point.y()
        if abs(x_pos - screen.left()) <= margin:
            x_pos = screen.left()
        if abs((x_pos + self.width()) - (screen.right() + 1)) <= margin:
            x_pos = screen.right() - self.width() + 1
        if abs(y_pos - screen.top()) <= margin:
            y_pos = screen.top()
        if abs((y_pos + self.height()) - (screen.bottom() + 1)) <= margin:
            y_pos = screen.bottom() - self.height() + 1
        return QPoint(x_pos, y_pos)

    def save_window_position(self):
        if self.isVisible():
            self.settings.update({"window_x": self.x(), "window_y": self.y()})

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            target = event.globalPosition().toPoint() - self.drag_offset
            self.move(self._snap_point(target))
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.move(self._snap_point(self.pos()))
            self.save_window_position()
            event.accept()

    def contextMenuEvent(self, _event):
        menu = QMenu(self)
        menu.setStyleSheet(MENU_QSS)
        items = [
            ("设置", self.request_settings.emit),
            ("临时隐藏", self.request_temporary_hide.emit),
            ("切换键盘布局", self.request_toggle_layout.emit),
            ("显示/隐藏小熊", self.request_toggle_cat.emit),
            ("显示/隐藏键盘", self.request_toggle_keyboard.emit),
        ]
        for text, callback in items:
            action = QAction(text, menu)
            action.triggered.connect(callback)
            menu.addAction(action)
        menu.addSeparator()
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.request_quit.emit)
        menu.addAction(quit_action)
        menu.exec(QCursor.pos())

    def closeEvent(self, event):
        self.save_window_position()
        super().closeEvent(event)
