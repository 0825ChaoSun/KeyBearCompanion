from pathlib import Path
import shutil

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_DIR = PROJECT_ROOT / "assets" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "qin_pack_assets" / "assets" / "processed"

BEAR_IMAGES = [
    "bear_peek_idle.png",
    "bear_peek_press_left.png",
    "bear_peek_press_right.png",
    "bear_peek_sleep.png",
    "bear_peek_wow.png",
    "bear_peek_smile.png",
    "bear_peek_happy.png",
    "bear_peek_sad.png",
]


def _resize_to_width(image, width):
    if image.width <= width:
        return image.copy()
    height = max(1, round(image.height * width / image.width))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def _save_png(image, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, "PNG", optimize=True, compress_level=9)


def _copy_ico():
    source = SOURCE_DIR / "app_icon.ico"
    target = OUTPUT_DIR / "app_icon.ico"
    if source.exists():
        shutil.copy2(source, target)


def prepare_qin_assets():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR.parent.parent)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name in BEAR_IMAGES:
        source = SOURCE_DIR / name
        if not source.exists():
            print(f"[qin] missing {source}")
            continue
        with Image.open(source) as image:
            optimized = _resize_to_width(image.convert("RGBA"), 384)
            _save_png(optimized, OUTPUT_DIR / name)
            print(f"[qin] {name}: {image.size} -> {optimized.size}")

    keyboard_source = SOURCE_DIR / "keyboard.png"
    if keyboard_source.exists():
        with Image.open(keyboard_source) as image:
            optimized = _resize_to_width(image.convert("RGBA"), 720)
            _save_png(optimized, OUTPUT_DIR / "keyboard.png")
            print(f"[qin] keyboard.png: {image.size} -> {optimized.size}")

    _copy_ico()

    original_size = sum(p.stat().st_size for p in SOURCE_DIR.glob("*.png") if p.name != "app_icon.png")
    qin_size = sum(p.stat().st_size for p in OUTPUT_DIR.glob("*.png"))
    print(f"[qin] processed png total: {original_size / 1024 / 1024:.2f} MB -> {qin_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    prepare_qin_assets()
