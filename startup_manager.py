import sys
from pathlib import Path


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "KeyBearCompanion"


class StartupManager:
    """Optional current-user Windows startup registration."""

    def __init__(self, app_path=None):
        if app_path is not None:
            self.app_path = Path(app_path)
        elif getattr(sys, "frozen", False):
            self.app_path = Path(sys.executable)
        else:
            self.app_path = Path(__file__).resolve().parent / "main.py"

    @staticmethod
    def build_startup_command(app_path):
        path = Path(app_path).resolve()
        if path.suffix.lower() == ".exe":
            return f'"{path}"'
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        return f'"{pythonw}" "{path}"'

    def is_available(self):
        return sys.platform.startswith("win")

    def set_enabled(self, enabled):
        if not self.is_available():
            return False, "开机启动只支持 Windows。"
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, self.build_startup_command(self.app_path))
                else:
                    try:
                        winreg.DeleteValue(key, VALUE_NAME)
                    except FileNotFoundError:
                        pass
            return True, "开机启动设置已更新。"
        except OSError as exc:
            return False, f"无法更新开机启动：{exc}"
