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


### Running tests
```
py -m unittest discover -s tests
```
___

## Template
[Template directory](VXTool_template) presents minimal project structure. Its [settings file](VXTool_template/settings.json) contains all settings needed for launch. [Callback file](VXTool_template/callback.py) is your sandbox.\
To create a new project from this template use:
```
py -m VXTool ./path/to_the_new/project/ create
```
A font file `UniVGA16.ttf` is provided in the template project. \
You may add your `*.ttf` font into the project directory and specify its name in `settings.json` under `["APP"]["preload_fonts"]`.

### UniVGA16 font 
Template project and examples contain `UniVGA16.ttf` font file. The file originally can be accessed [here](https://github.com/mirror/reactos/blob/c6d2b35ffc91e09f50dfb214ea58237509329d6b/reactos/media/fonts/UniVGA16.ttf) under attached [license](https://github.com/mirror/reactos/tree/master/reactos/media/fonts/doc/UniVGA). Originally created by [Dmitry Bolkhovityanov](https://www.inp.nsk.su/~bolkhov/files/fonts/univga/). The font is also a part of [reactOS](https://reactos.org/). 

## Guide
### Shortcuts
- `CTRL + Q` - quit
- `CTRL + S` - screenshot, saves into out/*.png files
### Follow examples
Not all examples aren't basic or concise. Some of them act as a documentation :)
- [colors](examples/color/callback.py) - Use text with colors to draw a static picture.
- [block_size](examples/block_size/callback.py) - Why do you need to and how to set block_size.
- [animation](examples/animation/callback.py) - Simple animated dot.Letter changing, moving.
- [stress](examples/stress/callback.py) - Primitive system level benchmark.
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

### System
#### Entities
- Main process
- - App
- - TextRender
- Callback (process)
#### Startup
|App|TextRender|Callback|
|:-:|:-:|:-:|
|Create window, font preload|||
|Create TextRender object|||
||Create render queue||
|Create event queue|||
|Spawn and start Callback|||
|Gives Callback access to TextRender's render queue||Has access to render queue|
|||Start Callback Loop|
#### Main Loop
|App|TextRender|
|:-:|:-:|
|Capture events from pygame||
|Execute any shortcuts pressed||
|Put events on event queue||
||Get entry from render queue|
||Process entry|

## TODO:
- get rid of widgets, just single text render (yes just do it)
- implement properly, document and test sync variants
- backcolor transparency isn't transparent
- sending multiple times from callback in the same frame implies continue flag, no need for that
- a difference between clear and backcolor
- default settings values
- should render queue be divided into commands and data?
- is blitting from a tileset faster than multiple surfaces?
- Loading png tilesets
- Position as (pygame.math.Vector2)
- cleaning up util ( constistency, remember about pygame Vector and Rect)
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