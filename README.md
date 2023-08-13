# VXTool
### Workflow tool for rendering text-based, animated grid.

Based on PyGame. Recording uses system call `ffmpeg` for stitching frames into video, but it's not needed for rendering `.png` images.

## Windows | Use source code in a virtual environment 
```
py -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
py -m VXTool template
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
[Template directory](template) presents minimal example of what's going on in here. Its [settings file](template/settings.json) contains all settings needed for launch. [Callback file](template/callback.py) is your sandbox. By putting these two files and your desired font into a directory, you create valid project.
___

### General notes
- Callback doesn't send whole buffer, only pos and hash list 
- Hash to Dot dict being held by TextRender.
- Callback holds its own hash to dot and sends updates
- 
- Main spawns App and Callback
#### Diff idea
- Slow.
- TextRender has internal Buffer. 
- Callback submits a diff to the queue, TextRender blits needed dots.
#### Sync
- App gathers events every window frame, while displaying last available TextRender surface.
- (didnt try not waiting) Callback chooses to wait or not for new InputFrame.
#### Dot
- TextRender font lookup by fontname and size.

## TODO:
- allow for adding multiple widgets
- document and test sync variants
- handle mouse events (screen_to_grid)
- Buffer.advance for animation
- Position as (pygame.math.Vector2)
- Loading png tilesets
- Interface:
- - pause/play/reload
- Live music performance:
- - spectral analysis
- - midi input 