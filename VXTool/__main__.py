import json
from pathlib import Path
from sys import argv, path
from collections import OrderedDict
from enum import Enum, auto

from .app import App
from .project import load_project, ProjectContext
from .font import FontBank

class LAUNCH_MSG(Enum):
    NO_SETTINGS_FILE = auto()
    NO_CALLBACK_FILE = auto()
    TASK_FAIL = auto()
    TASK_SUCCESS = auto()
    CALLBACK_FAIL = auto()

def _main():
    # first argument is read as a directory to specified project
    project_dir: Path = Path(argv[1]) 

    project: ProjectContext = load_project(project_dir)

    app = App()

    app.run(project)

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
    _main()
