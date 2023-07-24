from json import load
from pathlib import Path
from sys import argv, path
from collections import OrderedDict

from .app import _app
from .core import Color

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
    settings = project_dir / 'settings.json'
    with open(settings, 'r') as file:
        data = load(file, object_pairs_hook = OrderedDict)
        data['USER'].update(_SETTINGS['USER'])
        _SETTINGS.update(data)

    if "COLORS" in _SETTINGS["USER"]:
        colors = OrderedDict()
        for color_name, rgba in _SETTINGS["USER"]["COLORS"].items():
            colors[color_name] = Color(*rgba)
        _SETTINGS["USER"]["COLORS"] = colors

    _SETTINGS['TASKS']: dict = {
        'movie': _movie_task_call
    }
    
    if len(argv) > 2 and argv[2] in _SETTINGS['TASKS'].keys():
        call = _SETTINGS['TASKS'].get(argv[2], None)
        if call: call(_SETTINGS)
        return 2

    try:
        path.append(project_dir.as_posix())
        from callback import Callback
        assert Callback
        _SETTINGS['APP']['_callback'] = Callback
    except (ImportError, AssertionError) as e:
        print(e.msg)
        return 3

    render_size = _SETTINGS['APP']['render_size']
    full_res = _SETTINGS['TEXT_RENDER']['full_res']
    shape = _SETTINGS['TEXT_RENDER']['shape']

    _app(_SETTINGS)

    for task in _SETTINGS['APP']['end_tasks']:
        call = _SETTINGS['TASKS'][task]
        if call: call(_SETTINGS)

# Tasks
def _movie_task_str(settings: OrderedDict) -> str:
    """this is ffmpeg sequence that worked for me"""
    fps = settings['APP']['FPS']
    out_dir = settings['USER']['out_dir']
    return f'ffmpeg -framerate {fps} -i ' + (out_dir / f'frame_%05d.png').as_posix() + ' -c:v libx264 -pix_fmt yuv420p -vf scale=out_color_matrix=bt709 -r 60 ' + (out_dir / 'movie.mp4').as_posix()

def _movie_task_call(settings: OrderedDict, *args):
    from os import system
    system(_movie_task_str(settings))

if __name__ == '__main__':
    _main()
