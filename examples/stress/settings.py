from pathlib import Path

from VXTool.core import Color
from VXTool.font import FontInfo

BASE_DIR = Path(__file__).parent

CONFIG = {
    "project_dir": BASE_DIR,
    "backcolor": Color(0, 0, 0),
    "full_res": (720, 720),
    "shape": (64, 64),
    "render_size": (720, 720),
    "FPS": 60,
}

FONTS = [
    FontInfo(BASE_DIR/"UniVGA16.ttf", 16, "primary"),
]

colors = {
    "RED": Color(255, 0, 0),
    "GREEN": Color(0, 255, 0),
    "BLUE": Color(0, 0, 255)
}