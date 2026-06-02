from collections import deque
from pathlib import Path
import sys

from PIL import Image

from path_utils import resource_path, user_data_path

YIER_DIR = resource_path("yier_assets")
LEGACY_YIER_DIR = resource_path("一二形象")
SOURCE_DIRS = [resource_path("assets/source"), YIER_DIR, LEGACY_YIER_DIR, resource_path("assets")]
SOURCE_PROCESSED_DIR = resource_path("assets/processed")
WRITABLE_PROCESSED_DIR = user_data_path("assets/processed")
PROCESSED_DIR = WRITABLE_PROCESSED_DIR if hasattr(sys, "_MEIPASS") else SOURCE_PROCESSED_DIR

STATE_FILES = {
    "idle": ("bear_idle.png", "bear_peek_idle.png"),
    "press_left": ("bear_press_left.png", "bear_peek_press_left.png"),
    "press_right": ("bear_press_right.png", "bear_peek_press_right.png"),
    "sleep": ("bear_sleep.png", "bear_peek_sleep.png"),
    "wow": ("bear_wow.png", "bear_peek_wow.png"),
    "smile": ("bear_smile.png", "bear_peek_smile.png"),
    "happy": ("bear_happy.png", "bear_peek_happy.png"),
    "sad": ("bear_sad.png", "bear_peek_sad.png"),
}

KEYBOARD_SOURCE = "keyboard.png"
KEYBOARD_OUTPUT = "keyboard.png"


def _find_source(filename):
    for directory in SOURCE_DIRS:
        path = directory / filename
        if path.exists():
            return path
    return None


def _color_distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def _edge_palette(pixels, width, height):
    points = []
    step = max(1, min(width, height) // 80)
    for x in range(0, width, step):
        points.append(pixels[x, 0][:3])
        points.append(pixels[x, height - 1][:3])
    for y in range(0, height, step):
        points.append(pixels[0, y][:3])
        points.append(pixels[width - 1, y][:3])

    # Keep the palette small while still allowing softly varied backgrounds.
    palette = []
    for color in points:
        if not any(_color_distance(color, existing) <= 8 for existing in palette):
            palette.append(color)
    return palette[:64]


def _is_background_like(color, palette, tolerance):
    if color[3] == 0:
        return True
    rgb = color[:3]
    near_edge = any(_color_distance(rgb, bg) <= tolerance for bg in palette)
    near_white_background = rgb[0] >= 246 and rgb[1] >= 244 and rgb[2] >= 238
    return near_edge or near_white_background


def remove_connected_background_only(input_path, output_path, tolerance=28):
    """Remove only background pixels connected to an image edge.

    This intentionally does not make every white pixel transparent. Cream body
    areas and white keycaps are preserved unless they are edge-connected and
    close to the detected edge background colors.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)
    rgba = Image.open(input_path).convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    palette = _edge_palette(pixels, width, height)

    visited = bytearray(width * height)
    background = bytearray(width * height)
    queue = deque()

    def index(x, y):
        return y * width + x

    def enqueue_if_bg(x, y):
        idx = index(x, y)
        if visited[idx]:
            return
        visited[idx] = 1
        if _is_background_like(pixels[x, y], palette, tolerance):
            background[idx] = 1
            queue.append((x, y))

    for x in range(width):
        enqueue_if_bg(x, 0)
        enqueue_if_bg(x, height - 1)
    for y in range(height):
        enqueue_if_bg(0, y)
        enqueue_if_bg(width - 1, y)

    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                enqueue_if_bg(nx, ny)

    out_pixels = rgba.load()
    for y in range(height):
        row = y * width
        for x in range(width):
            if background[row + x]:
                r, g, b, _a = out_pixels[x, y]
                out_pixels[x, y] = (r, g, b, 0)
            else:
                r, g, b, _a = out_pixels[x, y]
                out_pixels[x, y] = (r, g, b, 255)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(output_path)
    return output_path


def process_keyboard(overwrite=False):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output = PROCESSED_DIR / KEYBOARD_OUTPUT
    if output.exists() and not overwrite:
        return output
    source = _find_source(KEYBOARD_SOURCE)
    if source is None:
        print(f"[KeyBear] 缺少键盘源图: {KEYBOARD_SOURCE}")
        return None
    return remove_connected_background_only(source, output, tolerance=34)


def process_assets(overwrite=False):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for state, (source_name, output_name) in STATE_FILES.items():
        output = PROCESSED_DIR / output_name
        if output.exists() and not overwrite:
            outputs[state] = output
            continue
        source = _find_source(source_name)
        if source is None:
            print(f"[KeyBear] 缺少源图: {source_name}")
            continue
        outputs[state] = remove_connected_background_only(source, output, tolerance=28)

    keyboard = process_keyboard(overwrite=overwrite)
    if keyboard is not None:
        outputs["keyboard"] = keyboard
    return outputs


if __name__ == "__main__":
    results = process_assets(overwrite=True)
    for state, path in results.items():
        print(f"{state}: {path}")
