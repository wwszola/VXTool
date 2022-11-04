# text_render 
### Single file tool for rendering text-based animation grid.
Based on PyGame. Recording uses system call `ffmpeg` for stitching frames into video, but it's not needed for rendering.

`py text_render.py template`

[Template directory](template) represents empty project. Its [settings file](template/settings.json) contains all settings needed for launch. [Callback file](template/callback.py) is your sandbox. By putting these two files and your desired font into a directory, you create valid project.

## Font
Fonts used need to be fixed width. Place `*.ttf` file in your project directory. Settings define `font_name` and `font_size`.