from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from path_utils import resource_path, user_data_path

ASSETS_DIR = resource_path("assets")
USER_ASSETS_DIR = user_data_path("assets/user")
GENERATED_ASSETS_DIR = user_data_path("assets/generated")
SOURCE_DIR = resource_path("assets/source")
YIER_ASSETS_DIR = resource_path("yier_assets")
LEGACY_YIER_ASSETS_DIR = resource_path("一二形象")
PROCESSED_DIR = resource_path("assets/processed")
CANVAS_SIZE = (256, 220)
SCALE = 4
DRAW_SIZE = (CANVAS_SIZE[0] * SCALE, CANVAS_SIZE[1] * SCALE)

REQUIRED_ASSETS = {
    "idle": "bear_idle.png",
    "press_left": "bear_press_left.png",
    "press_right": "bear_press_right.png",
    "sleep": "bear_sleep.png",
    "wow": "bear_wow.png",
    "smile": "bear_smile.png",
    "happy": "bear_happy.png",
    "sad": "bear_sad.png",
}

SOURCE_ALIASES = {
    "idle": ["bear_peek_idle.png", "bear_idle.png", "站立.png", "cat_idle.png"],
    "press_left": ["bear_peek_press_left.png", "bear_press_left.png", "左手按下.png", "cat_press_left.png"],
    "press_right": ["bear_peek_press_right.png", "bear_press_right.png", "右手按下.png", "cat_press_right.png"],
    "sleep": ["bear_peek_sleep.png", "bear_sleep.png", "睡觉.png", "cat_sleep.png"],
    "wow": ["bear_peek_wow.png", "bear_wow.png", "哇哦.png", "cat_surprised.png"],
    "smile": ["bear_peek_smile.png", "bear_smile.png", "微笑.png", "cat_blink.png"],
    "happy": ["bear_peek_happy.png", "bear_happy.png", "开心.png", "cat_happy.png"],
    "sad": ["bear_peek_sad.png", "bear_sad.png", "伤心.png", "cat_angry_1.png"],
}


def _box(box):
    return tuple(int(value * SCALE) for value in box)


def _draw_fallback_bear(state):
    image = Image.new("RGBA", DRAW_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    outline = "#6D513F"
    cream = "#FFF2D8"
    brown = "#D9AD7C"
    pink = "#F4A3AE"
    blush = "#F8C6C2"
    ink = "#3B2A22"

    def ellipse(box, fill, outline_color=None, width=1):
        draw.ellipse(_box(box), fill=fill, outline=outline_color, width=width * SCALE)

    def rounded(box, radius, fill, outline_color=None, width=1):
        draw.rounded_rectangle(_box(box), radius=radius * SCALE, fill=fill, outline=outline_color, width=width * SCALE)

    head_y = 34 if state != "sleep" else 64
    body_y = 112 if state != "sleep" else 128
    ellipse((58, 188, 198, 210), "#6b4b3324")
    rounded((76, body_y, 180, 178), 36, cream, outline, 4)
    ellipse((55, head_y + 8, 95, head_y + 48), brown, outline, 4)
    ellipse((161, head_y + 8, 201, head_y + 48), brown, outline, 4)
    ellipse((52, head_y + 28, 204, head_y + 134), cream, outline, 4)
    ellipse((72, head_y + 38, 111, head_y + 68), brown)
    ellipse((145, head_y + 38, 184, head_y + 68), brown)

    left_y = 154 + (13 if state == "press_left" else 0)
    right_y = 154 + (13 if state == "press_right" else 0)
    rounded((70, left_y, 116, left_y + 34), 14, cream, outline, 3)
    rounded((140, right_y, 186, right_y + 34), 14, cream, outline, 3)

    eye_y = head_y + 74
    if state in {"sleep", "smile", "happy"}:
        draw.arc(_box((87, eye_y - 3, 113, eye_y + 17)), 0, 180, fill=ink, width=3 * SCALE)
        draw.arc(_box((143, eye_y - 3, 169, eye_y + 17)), 0, 180, fill=ink, width=3 * SCALE)
    elif state == "wow":
        ellipse((90, eye_y - 5, 109, eye_y + 18), ink)
        ellipse((147, eye_y - 5, 166, eye_y + 18), ink)
        ellipse((121, eye_y + 32, 136, eye_y + 48), ink)
    elif state == "sad":
        draw.arc(_box((88, eye_y, 112, eye_y + 16)), 200, 340, fill=ink, width=3 * SCALE)
        draw.arc(_box((144, eye_y, 168, eye_y + 16)), 200, 340, fill=ink, width=3 * SCALE)
        ellipse((100, eye_y + 15, 106, eye_y + 30), "#8FC7E8")
        ellipse((156, eye_y + 15, 162, eye_y + 30), "#8FC7E8")
    else:
        ellipse((91, eye_y - 5, 108, eye_y + 18), ink)
        ellipse((148, eye_y - 5, 165, eye_y + 18), ink)

    ellipse((72, eye_y + 18, 101, eye_y + 35), blush)
    ellipse((155, eye_y + 18, 184, eye_y + 35), blush)
    draw.polygon([_box((124, eye_y + 22, 124, eye_y + 22))[0:2], _box((132, eye_y + 22, 132, eye_y + 22))[0:2], _box((128, eye_y + 29, 128, eye_y + 29))[0:2]], fill=pink)
    if state == "sleep":
        draw.text((190 * SCALE, 42 * SCALE), "Zz", fill=outline)

    return image.filter(ImageFilter.GaussianBlur(0.12)).resize(CANVAS_SIZE, Image.Resampling.LANCZOS)


def find_user_asset(state, assets_dir=ASSETS_DIR):
    assets_path = Path(assets_dir)
    roots = []
    if assets_path.resolve() == ASSETS_DIR.resolve():
        roots.extend([PROCESSED_DIR, SOURCE_DIR, YIER_ASSETS_DIR, LEGACY_YIER_ASSETS_DIR, USER_ASSETS_DIR])
    roots.append(assets_path)
    for root in roots:
        for filename in SOURCE_ALIASES[state]:
            path = root / filename
            if path.exists():
                return path
    return None


def generate_assets(assets_dir=ASSETS_DIR, overwrite=False):
    assets_path = Path(assets_dir)
    if assets_path != ASSETS_DIR or not ASSETS_DIR.exists():
        assets_path.mkdir(parents=True, exist_ok=True)
    if assets_path == ASSETS_DIR:
        USER_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    fallback_dir = GENERATED_ASSETS_DIR if assets_path == ASSETS_DIR else assets_path
    fallback_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for state, filename in REQUIRED_ASSETS.items():
        user_asset = find_user_asset(state, assets_path)
        if user_asset is not None and user_asset.name != filename:
            outputs[state] = user_asset
            continue
        bundled_path = assets_path / filename
        if bundled_path.exists() and not overwrite:
            outputs[state] = bundled_path
            continue
        path = fallback_dir / filename
        if overwrite or not path.exists():
            _draw_fallback_bear(state).save(path)
        outputs[state] = path
    return outputs
