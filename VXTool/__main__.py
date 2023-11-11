from pathlib import Path
import argparse
from shutil import copytree

from .app import App
from .project import load_project, ProjectContext

def _create_new_project(project_dir: Path):
    template_dir = Path(__file__).parent.parent / 'VXTool_template'
    copytree(template_dir, project_dir)

def _main():
    parser = argparse.ArgumentParser(prog="VXTool")
    parser.add_argument("project_dir", type=Path, help="path specyfing project directory")
    parser.add_argument("-c", "--create", action="store_true", help="create an empty project at project_dir")

    args = parser.parse_args()

    if args.create:
        _create_new_project(args.project_dir)
        return

    project: ProjectContext = load_project(args.project_dir)

    app = App()

    app.run(project)

# Tasks
# def _movie_task_str(settings: OrderedDict) -> str:
#     # this is ffmpeg sequence that worked for me
#     # compression, color formats may be adjustable
#     app_fps = settings['APP']['FPS']
#     movie_fps = 60
#     out_dir = settings['USER']['out_dir']
#     img_path = (out_dir / 'frame_%05d.png').as_posix()
#     movie_path = (out_dir / 'movie.mp4').as_posix()
#     return f'ffmpeg -framerate {app_fps} -i {img_path} -c:v libx264 -pix_fmt yuv420p -vf scale=out_color_matrix=bt709 -r {movie_fps} {movie_path}'

# def _movie_task_call(settings: OrderedDict, msgs: list[LAUNCH_MSG], *args):
#     if LAUNCH_MSG.NO_SETTINGS_FILE in msgs:
#         msgs.extend((LAUNCH_MSG.TASK_FAIL, "_movie_task_call"))
#         return
    
#     from os import system
#     system(_movie_task_str(settings))

#     msgs.extend((LAUNCH_MSG.TASK_SUCCESS, "_movie_task_call"))

if __name__ == '__main__':
    _main()
