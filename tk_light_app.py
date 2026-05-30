import random
import sys
import time
import tkinter as tk
from pathlib import Path

from keyboard_layout import KeyboardLayout
from keyboard_listener import KeyboardListener
from path_utils import resource_path


TRANSPARENT = "#010203"
APP_W = 640
APP_H = 470
KEYBOARD_W = 560
KEYBOARD_Y = 205
BEAR_SIZE = 250
BEAR_Y = 12

STATE_FILES = {
    "idle": "bear_peek_idle.png",
    "press_left": "bear_peek_press_left.png",
    "press_right": "bear_peek_press_right.png",
    "sleep": "bear_peek_sleep.png",
    "wow": "bear_peek_wow.png",
    "smile": "bear_peek_smile.png",
    "happy": "bear_peek_happy.png",
    "sad": "bear_peek_sad.png",
}


def _asset_path(name):
    qin_path = resource_path(f"qin_pack_assets/assets/processed/{name}")
    if qin_path.exists():
        return qin_path
    return resource_path(f"assets/processed/{name}")


class KeyBearTkLight:
    """Ultra-light Tk runtime used only for the smallest packaged build."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KeyBear Companion")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", TRANSPARENT)
        self.root.configure(bg=TRANSPARENT)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{APP_W}x{APP_H}+{screen_w - APP_W - 50}+{screen_h - APP_H - 80}")

        self.canvas = tk.Canvas(
            self.root,
            width=APP_W,
            height=APP_H,
            bg=TRANSPARENT,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.layout = KeyboardLayout(density="clean")
        self.pressed = set()
        self.state = "idle"
        self.overlay_until = 0.0
        self.restore_due = 0.0
        self.last_input = time.monotonic()
        self.idle_state = "idle"
        self.next_idle_shuffle = 0.0
        self.recent_presses = []
        self.drag_start = None

        self.images = {}
        self.bear_images = {}
        self.keyboard_image = None
        self._load_images()
        self._build_canvas()
        self._bind_ui()

        self.listener = KeyboardListener(self.on_key_down, self.on_key_up, debug=False)
        self.listener.start()
        self._schedule_idle_shuffle()
        self.root.after(80, self.tick)

    def _load_images(self):
        for state, file_name in STATE_FILES.items():
            path = _asset_path(file_name)
            if not path.exists():
                path = _asset_path(STATE_FILES["idle"])
            img = tk.PhotoImage(file=str(path))
            if img.width() > BEAR_SIZE:
                # The qin assets are 384px. Subsample keeps Tk dependency-free and
                # is enough for this intentionally tiny build.
                img = img.subsample(max(1, round(img.width() / BEAR_SIZE)))
            self.bear_images[state] = img
        keyboard_path = _asset_path("keyboard.png")
        self.keyboard_image = tk.PhotoImage(file=str(keyboard_path))
        if self.keyboard_image.width() > KEYBOARD_W:
            self.keyboard_image = self.keyboard_image.subsample(max(1, round(self.keyboard_image.width() / KEYBOARD_W)))

    def _build_canvas(self):
        self.bear_x = APP_W // 2
        self.keyboard_x = APP_W // 2
        self.bear_item = self.canvas.create_image(
            self.bear_x,
            BEAR_Y,
            image=self.bear_images["idle"],
            anchor="n",
        )
        self.keyboard_item = self.canvas.create_image(
            self.keyboard_x,
            KEYBOARD_Y,
            image=self.keyboard_image,
            anchor="n",
        )
        self.highlight_items = {}

    def _bind_ui(self):
        self.root.bind("<ButtonPress-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._drag)
        self.root.bind("<Button-3>", self._show_menu)
        self.menu = tk.Menu(self.root, tearoff=False)
        self.menu.add_command(label="退出", command=self.quit)

    def _start_drag(self, event):
        self.drag_start = (event.x_root, event.y_root, self.root.winfo_x(), self.root.winfo_y())

    def _drag(self, event):
        if not self.drag_start:
            return
        sx, sy, wx, wy = self.drag_start
        self.root.geometry(f"+{wx + event.x_root - sx}+{wy + event.y_root - sy}")

    def _show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def on_key_down(self, label):
        self.last_input = time.monotonic()
        self.pressed.add(label)
        self._draw_highlights()
        now = time.monotonic()
        self.recent_presses = [stamp for stamp in self.recent_presses if now - stamp < 1.2]
        self.recent_presses.append(now)

        if label == "Backspace":
            self._set_overlay("sad", 1.0)
        elif label in {"S", "C", "V"} and ("LeftCtrl" in self.pressed or "RightCtrl" in self.pressed):
            self._set_overlay("happy", 0.9)
        elif not (len(label) == 1 and label.isalnum()):
            self._set_overlay("wow", 0.8)
        else:
            self._set_state("press_left" if self.layout.key_side(label) == "left" else "press_right")
            self.restore_due = now + 0.18

    def on_key_up(self, label):
        self.pressed.discard(label)
        self._draw_highlights()
        self.restore_due = time.monotonic() + 0.12

    def _set_overlay(self, state, seconds):
        self.overlay_until = time.monotonic() + seconds
        self._set_state(state)

    def _set_state(self, state):
        if state == self.state:
            return
        self.state = state
        self.canvas.itemconfigure(self.bear_item, image=self.bear_images[state])
        if state == "sleep":
            self.canvas.tag_raise(self.bear_item)
        else:
            self.canvas.tag_lower(self.bear_item, self.keyboard_item)

    def _schedule_idle_shuffle(self):
        self.next_idle_shuffle = time.monotonic() + random.uniform(3, 7)

    def _draw_highlights(self):
        for item in self.highlight_items.values():
            self.canvas.delete(item)
        self.highlight_items.clear()
        if not self.pressed:
            return
        kw = self.keyboard_image.width()
        kh = self.keyboard_image.height()
        left = self.keyboard_x - kw / 2
        top = KEYBOARD_Y
        for label in sorted(self.pressed):
            spec = self.layout.key_spec(label)
            if not spec:
                continue
            x1 = left + spec.x * kw
            y1 = top + spec.y * kh
            x2 = left + (spec.x + spec.w) * kw
            y2 = top + (spec.y + spec.h) * kh
            self.highlight_items[label] = self.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="#F6B6A8",
                outline="#E7B8AE",
                width=1,
            )
            self.canvas.tag_raise(self.highlight_items[label], self.keyboard_item)

    def tick(self):
        now = time.monotonic()
        if self.overlay_until and now < self.overlay_until:
            self.root.after(80, self.tick)
            return
        self.overlay_until = 0.0
        if self.pressed:
            self.root.after(80, self.tick)
            return
        if now - self.last_input > 180:
            self._set_state("sleep")
        elif self.restore_due and now < self.restore_due:
            pass
        elif now >= self.next_idle_shuffle:
            self.idle_state = random.choice(["idle", "smile", "happy"])
            self._schedule_idle_shuffle()
            self._set_state(self.idle_state)
        elif self.state in {"press_left", "press_right", "wow", "sad"}:
            self._set_state(self.idle_state)
        self.root.after(80, self.tick)

    def quit(self):
        try:
            self.listener.stop()
        finally:
            self.root.destroy()

    def run(self):
        self.root.mainloop()


def run():
    app = KeyBearTkLight()
    app.run()


if __name__ == "__main__":
    run()
