from json import load
from pathlib import Path
from sys import argv, path
from collections import OrderedDict
from enum import Enum, auto

from .app import _app
from .core import Color

class LAUNCH_MSG(Enum):
    NO_SETTINGS_FILE = auto()
    NO_CALLBACK_FILE = auto()
    TASK_FAIL = auto()
    TASK_SUCCESS = auto()
    CALLBACK_FAIL = auto()

def _main():
    project_dir: Path = Path(argv[1]) 
    out_dir = project_dir / 'out'
    print(project_dir)

    _SETTINGS = OrderedDict([
        ("USER", OrderedDict([
            ("fonts", {}),
            ("project_dir", project_dir),
            ("out_dir", out_dir)
        ]))
    ])
    msgs = []
    settings_path = project_dir / 'settings.json'
    try:
        with open(settings_path, 'r') as file:
            data = load(file, object_pairs_hook = OrderedDict)
            data['USER'].update(_SETTINGS['USER'])
            _SETTINGS.update(data)
    except FileNotFoundError as e:
        msgs.extend((LAUNCH_MSG.NO_SETTINGS_FILE, project_dir))

    if "COLORS" in _SETTINGS["USER"]:
        colors = OrderedDict()
        for color_name, rgba in _SETTINGS["USER"]["COLORS"].items():
            colors[color_name] = Color(*rgba)
        _SETTINGS["USER"]["COLORS"] = colors

    try:
        path.append(project_dir.as_posix())
        from callback import Callback
        assert Callback
        _SETTINGS['APP']['_callback'] = Callback
    except (ImportError, AssertionError) as e:
        msgs.extend((LAUNCH_MSG.NO_CALLBACK_FILE, project_dir))

    _SETTINGS['TASKS']: dict = {
        'movie': _movie_task_call,
        'create': _new_project_task_call
    }
    
    if len(argv) > 2 and argv[2] in _SETTINGS['TASKS'].keys():
        call = _SETTINGS['TASKS'].get(argv[2], None)
        if call: call(_SETTINGS, msgs)
        return msgs


    # render_size = _SETTINGS['APP']['render_size']
    # full_res = _SETTINGS['TEXT_RENDER']['full_res']
    # shape = _SETTINGS['TEXT_RENDER']['shape']

    if LAUNCH_MSG.NO_CALLBACK_FILE in msgs or LAUNCH_MSG.NO_SETTINGS_FILE in msgs:
        msgs.append(LAUNCH_MSG.CALLBACK_FAIL)
        return msgs

    _app(_SETTINGS)

    for task in _SETTINGS['APP']['end_tasks']:
        call = _SETTINGS['TASKS'][task]
        if call: call(_SETTINGS, msgs)

    return msgs

# Tasks
def _movie_task_str(settings: OrderedDict) -> str:
    """this is ffmpeg sequence that worked for me"""
    fps = settings['APP']['FPS']
    out_dir = settings['USER']['out_dir']
    return f'ffmpeg -framerate {fps} -i ' + (out_dir / f'frame_%05d.png').as_posix() + ' -c:v libx264 -pix_fmt yuv420p -vf scale=out_color_matrix=bt709 -r 60 ' + (out_dir / 'movie.mp4').as_posix()

def _movie_task_call(settings: OrderedDict, msgs: list[LAUNCH_MSG], *args):
    if LAUNCH_MSG.NO_SETTINGS_FILE in msgs:
        msgs.extend((LAUNCH_MSG.TASK_FAIL, "_movie_task_call"))
        return
    
    from os import system
    system(_movie_task_str(settings))

    msgs.extend((LAUNCH_MSG.TASK_SUCCESS, "_movie_task_call"))

def _new_project_task_call(settings: OrderedDict, msgs: list[LAUNCH_MSG], *args):
    if LAUNCH_MSG.NO_SETTINGS_FILE not in msgs:
        msgs.extend((LAUNCH_MSG.TASK_FAIL, "_new_project_task_call"))

    from os import mkdir, path
    project_dir = settings['USER']['project_dir']
    template_dir = Path(path.dirname(__file__), '..', 'VXTool_template')
    try:
        mkdir(project_dir)
        mkdir(project_dir / 'out')
        with open(template_dir / 'settings.json', 'rb') as template:
            with open(project_dir / 'settings.json', 'wb') as project:
                project.write(template.read())
        with open(template_dir / 'callback.py', 'rb') as template:
            with open(project_dir / 'callback.py', 'wb') as project:
                project.write(template.read())
        msgs.extend((LAUNCH_MSG.TASK_SUCCESS, "_new_project_task_call"))
    except (FileExistsError, FileNotFoundError, OSError) as e:
        print("Failed to create a new project due to error:")
        print(e)
        msgs.extend((LAUNCH_MSG.TASK_FAIL, "_new_project_task_call"))

if __name__ == '__main__':
    msgs = _main()
    print("VXTool launch messages", msgs)
