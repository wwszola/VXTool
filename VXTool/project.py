import importlib
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from sys import modules, path
from types import ModuleType

from .core import Color
from .font import FontInfo

CONFIG_DEFAULTS = {
    "backcolor": Color(0, 0, 0),
    "full_res": (512, 512),
    "shape": (16, 8),
    "render_size": (720, 720),
    "FPS": 30,
    "quit": -1,
    "record": (-1, -1),
    "real_time": False,
    "out_dir": Path("out"),
}


def get_out_dir(config: dict):
    out_dir: Path = config["out_dir"]
    if not out_dir.is_absolute():
        out_dir = config["project_dir"] / config["out_dir"]
    out_dir.mkdir(exist_ok=True)
    return out_dir


@dataclass
class ProjectContext:
    callback_module: ModuleType
    config: dict
    fonts_info: list[FontInfo]

    @property
    def project_dir(self):
        return self.config["project_dir"]

    @property
    def name(self):
        return self.config["project_dir"].name


def load_project(project_dir: Path):
    assert project_dir.is_dir()
    project_name = project_dir.name
    path.append(str(project_dir.parent))
    _top_level = importlib.import_module(project_name)
    callback = importlib.import_module(project_name + ".callback")
    settings = importlib.import_module(project_name + ".settings")

    config = deepcopy(CONFIG_DEFAULTS)
    config["project_dir"] = project_dir
    config.update(settings.CONFIG)
    config["out_dir"] = get_out_dir(config)

    fonts_info = settings.FONTS
    return ProjectContext(callback, config, fonts_info)


def unload_project(project: ProjectContext):
    project_name = project.name
    try:
        path.remove(str(project.project_dir))
        del modules[project_name]
        del modules[project_name + ".callback"]
        del modules[project_name + ".settings"]
    except ValueError:
        print(f"Project located at {project.project_dir} has not been loaded yet.")
