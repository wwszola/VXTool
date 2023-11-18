from pathlib import Path

from VXTool.core import Color
from VXTool.font import FontInfo

BASE_DIR = Path(__file__).parent

CONFIG = {
    "project_dir": BASE_DIR,
    "backcolor": Color(125, 125, 125),
    "full_res": (512, 256),
    "shape": (128, 64),
    "render_size": (512, 256),
    "FPS": 30,
}

FONTS = [
    FontInfo(BASE_DIR / "UniVGA16.ttf", 16, "primary"),
]
