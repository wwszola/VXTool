from pathlib import Path
from sys import path, modules
import importlib
from copy import deepcopy

from .font import FontInfo
from .core import Color

CONFIG_DEFAULTS = {
    "backcolor": Color(0, 0, 0),
    "full_res": (512, 512),
    "shape": (16, 8),
    "render_size": (720, 720),
    "FPS": 30,
    "quit": 0,
    "record": (0, 0),
    "real_time": False,
    "out_dir": Path("out"),
}

def get_out_dir(config: dict):
    out_dir = config["out_dir"]
    if out_dir.is_absolute:
        return out_dir
    else:
        return config["project_dir"] / config["out_dir"]

def load_project(project_dir: Path):
    if "callback" in modules or "settings" in modules:
        raise Exception("Unload project before trying to load another")
    path.append(str(project_dir))
    callback = importlib.import_module("callback")
    settings = importlib.import_module("settings")
    config = deepcopy(CONFIG_DEFAULTS)
    config["project_dir"] = project_dir
    config.update(settings.CONFIG)
    fonts_info = settings.FONTS
    return callback, config, fonts_info

def unload_project(project_dir: Path):
    project_dir = str(project_dir)
    if project_dir not in path:
        raise Exception(f"Project located at {project_dir} has not been loaded yet")
    path.remove(project_dir)
    del modules["callback"]
    del modules["settings"]
