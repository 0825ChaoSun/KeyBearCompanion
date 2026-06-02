from collections import deque
from pathlib import Path

from PIL import Image

from path_utils import resource_path


SOURCE_ICON = resource_path("yier_assets/icon.png")
LEGACY_SOURCE_ICON = resource_path("一二形象/图标.png")
PROCESSED_DIR = resource_path("assets/processed")
PROCESSED_PNG = PROCESSED_DIR / "app_icon.png"
PROCESSED_ICO = PROCESSED_DIR / "app_icon.ico"


def _dark_distance(color, target):
    return ((color[0] - target[0]) ** 2 + (color[1] - target[1]) ** 2 + (color[2] - target[2]) ** 2) ** 0.5


def remove_connected_dark_background(input_path, output_path, tolerance=42):
    """Remove only dark pixels connected to the image edges."""

    input_path = Path(input_path)
    output_path = Path(output_path)
    image = Image.open(input_path).convert("RGBA")
    pixels = image.load()
    width, height = image.size

    edge_samples = []
    step = max(1, min(width, height) // 96)
    for x in range(0, width, step):
        edge_samples.append(pixels[x, 0][:3])
        edge_samples.append(pixels[x, height - 1][:3])
    for y in range(0, height, step):
        edge_samples.append(pixels[0, y][:3])
        edge_samples.append(pixels[width - 1, y][:3])

    dark_edges = [color for color in edge_samples if max(color) < 96]
    background = dark_edges[:32] or [(0, 0, 0)]

    visited = bytearray(width * height)
    remove = bytearray(width * height)
    queue = deque()

    def index(x, y):
        return y * width + x

    def is_background(x, y):
        color = pixels[x, y]
        if color[3] == 0:
            return True
        rgb = color[:3]
        return max(rgb) < 130 and any(_dark_distance(rgb, bg) <= tolerance for bg in background)

    def enqueue(x, y):
        idx = index(x, y)
        if visited[idx]:
            return
        visited[idx] = 1
        if is_background(x, y):
            remove[idx] = 1
            queue.append((x, y))

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(height):
        enqueue(0, y)
        enqueue(width - 1, y)

    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                enqueue(nx, ny)

    for y in range(height):
        row = y * width
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if remove[row + x]:
                pixels[x, y] = (r, g, b, 0)
            elif a != 0:
                pixels[x, y] = (r, g, b, 255)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return output_path


def build_icon():
    source = SOURCE_ICON if SOURCE_ICON.exists() else LEGACY_SOURCE_ICON
    if not source.exists():
        print(f"[KeyBear] icon source not found: {SOURCE_ICON}")
        return None
    transparent_png = remove_connected_dark_background(source, PROCESSED_PNG)
    image = Image.open(transparent_png).convert("RGBA")
    image.save(PROCESSED_ICO, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"[KeyBear] icon png: {transparent_png}")
    print(f"[KeyBear] icon ico: {PROCESSED_ICO}")
    return PROCESSED_ICO


if __name__ == "__main__":
    build_icon()
