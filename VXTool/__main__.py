import json
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
    # first argument is read as a directory to specified project
    project_dir: Path = Path(argv[1]) 
    out_dir = project_dir / 'out'
    print(project_dir)

    # don't overwrite any of the defaults below
    # in your project's settings.json file 
    _SETTINGS = OrderedDict([
        ("USER", OrderedDict([
            ("fonts", {}),
            ("project_dir", project_dir),
            ("out_dir", out_dir)
        ]))
    ])
    msgs = []

    # tries to load settings and callback files first,
    # before checking for a command
    settings_path = project_dir / 'settings.json'
    try:
        with open(settings_path, 'r') as file:
            data = json.load(file, object_pairs_hook = OrderedDict)
            data['USER'].update(_SETTINGS['USER'])
            _SETTINGS.update(data)
    except FileNotFoundError as e:
        msgs.extend((LAUNCH_MSG.NO_SETTINGS_FILE, project_dir))

    # to properly load colors in settings file use "COLORS" attribute
    # ex. "USER": {"COLORS": {"WHITE": [0, 0, 0]}}
    if "COLORS" in _SETTINGS["USER"]:
        colors = OrderedDict()
        for color_name, rgba in _SETTINGS["USER"]["COLORS"].items():
            colors[color_name] = Color(*rgba)
        _SETTINGS["USER"]["COLORS"] = colors

    # your's callback.py file should include a class named Callback
    # inheriting from VXTool.callback.CallbackProcess
    try:
        path.append(project_dir.as_posix())
        from callback import Callback
        assert Callback
        _SETTINGS['APP']['_callback'] = Callback
    except (ImportError, AssertionError) as e:
        msgs.extend((LAUNCH_MSG.NO_CALLBACK_FILE, project_dir))

    _SETTINGS['TASKS']: dict = {
        'movie': _movie_task_call, # stitch rendered .png files into .mp4 movie
        'create': _new_project_task_call # creates new project from VXTool_template
    }

    # if you include more than one argument,
    # the default behaviour i.e. to launch your intended project and
    # execution of "end_tasks" specified in "APP" settings are ignored

    # second argument is name of the command/task you want to use
    if len(argv) > 2 and argv[2] in _SETTINGS['TASKS'].keys():
        call = _SETTINGS['TASKS'].get(argv[2], None)
        if call: 
            call(_SETTINGS, msgs)
        else:
            msgs.extend((LAUNCH_MSG.TASK_FAIL, f'unknown command {argv[2]}'))
        return msgs

    # app is able to launch when settings and callback files are loaded
    if LAUNCH_MSG.NO_CALLBACK_FILE in msgs or LAUNCH_MSG.NO_SETTINGS_FILE in msgs:
        msgs.append(LAUNCH_MSG.CALLBACK_FAIL)
        return msgs

    _app(_SETTINGS)

    # "end_tasks" may be specified which are commands to be executed
    # after successful _app launch 
    for task in _SETTINGS['APP']['end_tasks']:
        call = _SETTINGS['TASKS'][task]
        if call: call(_SETTINGS, msgs)

    return msgs

# Tasks
def _movie_task_str(settings: OrderedDict) -> str:
    # this is ffmpeg sequence that worked for me
    # compression, color formats may be adjustable
    app_fps = settings['APP']['FPS']
    movie_fps = 60
    out_dir = settings['USER']['out_dir']
    img_path = (out_dir / 'frame_%05d.png').as_posix()
    movie_path = (out_dir / 'movie.mp4').as_posix()
    return f'ffmpeg -framerate {app_fps} -i {img_path} -c:v libx264 -pix_fmt yuv420p -vf scale=out_color_matrix=bt709 -r {movie_fps} {movie_path}'

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
    from shutil import copyfile, SameFileError
    project_dir = settings['USER']['project_dir']
    template_dir = Path(path.dirname(__file__), '..', 'VXTool_template')
    try:
        mkdir(project_dir)
        mkdir(project_dir / 'out')
        copyfile(template_dir/'settings.json', project_dir/'settings.json')
        copyfile(template_dir/'callback.py', project_dir/'callback.py')
        copyfile(template_dir/'UniVGA16.ttf', project_dir/'UniVGA16.ttf')        
        msgs.extend((LAUNCH_MSG.TASK_SUCCESS, "_new_project_task_call"))
    except (SameFileError, OSError) as e:
        print("Failed to create a new project due to error:")
        print(e)
        msgs.extend((LAUNCH_MSG.TASK_FAIL, "_new_project_task_call"))

if __name__ == '__main__':
    msgs = _main()
    print("VXTool launch messages", msgs)
