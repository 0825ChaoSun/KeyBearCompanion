import random
import time

from PySide6.QtCore import QObject, QTimer


OVERLAY_PRIORITY = {
    None: 0,
    "smile": 2,
    "happy": 3,
    "wow": 4,
    "sad": 5,
}


class AnimationController(QObject):
    """Full-sprite state controller with no floating, bounce, or scale motion."""

    def __init__(self, window, settings, idle_detector, parent=None):
        super().__init__(parent)
        self.window = window
        self.settings = settings
        self.idle_detector = idle_detector
        self.current_press_side = None
        self.last_input = time.monotonic()
        self.overlay_until = 0.0
        self.overlay_state = None
        self.restore_due = 0.0
        self.idle_state = "idle"
        self.next_idle_shuffle = 0.0
        self.timer = QTimer(self)
        self.timer.setInterval(80)
        self.timer.timeout.connect(self.tick)

    def start(self):
        self.set_overlay("smile", 1000)
        self._schedule_idle_shuffle()
        self.timer.start()

    def mark_input(self):
        self.last_input = time.monotonic()

    def press(self, side):
        self.mark_input()
        self.current_press_side = side
        self.overlay_until = 0.0
        self.overlay_state = None
        self.window.cat.set_press_state(side)

    def release(self, side=None):
        if side is None or side == self.current_press_side:
            self.current_press_side = None
            self.restore_due = time.monotonic() + 0.12

    def trigger_fast_typing(self):
        # Fast typing no longer moves the image. Higher-level key logic can still
        # choose wow/happy overlays without adding positional animation.
        self.mark_input()

    def set_overlay(self, state, ms=1000):
        if OVERLAY_PRIORITY[state] < OVERLAY_PRIORITY.get(self.overlay_state, 0) and time.monotonic() < self.overlay_until:
            return
        self.overlay_state = state
        self.overlay_until = time.monotonic() + ms / 1000
        self.window.cat.set_state(state)

    def _schedule_idle_shuffle(self):
        low = self.settings.get("idle_expression_min_seconds")
        high = self.settings.get("idle_expression_max_seconds")
        self.next_idle_shuffle = time.monotonic() + random.uniform(low, high)

    def _choose_idle_state(self):
        if not self.settings.get("idle_expression_shuffle"):
            return "idle"
        self.idle_state = random.choice(["idle", "smile", "happy"])
        self._schedule_idle_shuffle()
        return self.idle_state

    def tick(self):
        now = time.monotonic()

        if self.current_press_side:
            self.window.cat.set_press_state(self.current_press_side)
            return
        if self.overlay_state and now < self.overlay_until:
            self.window.cat.set_state(self.overlay_state)
            return
        self.overlay_state = None

        idle_seconds = now - self.last_input
        try:
            idle_seconds = max(idle_seconds, self.idle_detector.get_idle_seconds())
        except Exception:
            pass

        if self.settings.get("sleep_enabled") and idle_seconds > self.settings.get("sleep_wait_seconds"):
            self.window.cat.set_state("sleep")
            return
        if self.restore_due and now < self.restore_due:
            return
        if now >= self.next_idle_shuffle:
            self.window.cat.set_state(self._choose_idle_state())
        else:
            self.window.cat.set_state(self.idle_state)
