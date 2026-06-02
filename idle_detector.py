import ctypes
import sys
import time


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


class IdleDetector:
    """Reports system idle seconds on Windows, with a safe fallback elsewhere."""

    def __init__(self):
        self.created_at = time.monotonic()

    def get_idle_seconds(self):
        if not sys.platform.startswith("win"):
            return 0
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(info)
        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
            return 0
        millis = ctypes.windll.kernel32.GetTickCount() - info.dwTime
        return max(0, millis / 1000)
