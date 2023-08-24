# VXTool
### Workflow tool for rendering text-based, animated grid.

Based on PyGame. Recording uses system call `ffmpeg` for stitching frames into video, but it's not needed for rendering `.png` images.

## Windows | Use source code in a virtual environment 
```
py -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
py -m VXTool examples/color
```
### Build a package
To build the package make sure you also have `build` installed. Config is written in `pyproject.toml`.
```
pip install build
py -m build
```
### Install the wheel
Building the package with `build` tool creates a `dist` directory containing files `VXTool-0.1.tar.gz`, `VXTool-0.1-py3-none-any.whl`. Install using pip specyfing `.whl` file. 
___

## Template
[Template directory](VXTool_template) presents minimal project structure. Its [settings file](VXTool_template/settings.json) contains all settings needed for launch. [Callback file](VXTool_template/callback.py) is your sandbox. By putting these two files and your desired font into a directory, you create valid project. \
To create a new project from this template use:
```
py -m VXTool ./path/to_the_new/project/ create
```
You will need to add your `*.ttf` font into the project directory and specify its name in `settings.json` in `["APP"]["preload_fonts]` dictionary.
#### TODO: What font under what license should we include here.
___

## General notes
- Main spawns App and Callback
#### What is sent through render queue
- Callback doesn't send whole buffer, only pos and hash list 
- Hash to Dot dict being held by TextRender.
- Callback holds its own hash to dot and sends updates
#### Diff idea
- Slow.
- TextRender has internal Buffer. 
- Callback submits a diff to the queue, TextRender blits needed dots.
#### Sync
- App gathers events every window frame, while displaying last available TextRender surface.

#### Dot
- TextRender font lookup by fontname and size.

#### Animation
- Dots do not need to be immutable
- Changing dot's position requires removing from the buffer and putting again after change
- variant / creation, duplication of animated dots is important
- reminder: this doesn't need to be turing complete
- how to spawn the falling star

## TODO:
- allow for positioning widgets
- implement properly, document and test sync variants
- handle mouse events (screen_to_grid)
- backcolor transparency isn't transparent
- Loading png tilesets
- Position as (pygame.math.Vector2)
### Sync
- (__didnt try not waiting__) Callback chooses to wait or not for new InputFrame.
- widget discards callback frames up to the last one if their counters don't match 
- __Moving__ the window causes to crash because of some blocking timeout?

### Ideas
- Interface:
- - pause/play/reload
- Live music performance:
- - spectral analysis
- - midi input 