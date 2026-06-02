from pathlib import Path

import pet_keyboard_window
from app import run


if __name__ == "__main__":
    print(f"Running main.py: {Path(__file__).resolve()}")
    print(f"Loaded pet_keyboard_window.py: {Path(pet_keyboard_window.__file__).resolve()}")
    print(f"Current working directory: {Path.cwd()}")
    run()
    
