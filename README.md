# text_render 
## Workflow tool for rendering text-based, animated grid.
#### This is highly experimental right now. I'v done [some animations](https://www.instagram.com/wwszola_art) to test this. It works but may be not consistent and is not fast at all.
____
Based on PyGame. Recording uses system call `ffmpeg` for stitching frames into video, but it's not needed for rendering.

`py text_render.py template`

[Template directory](template) represents empty project. Its [settings file](template/settings.json) contains all settings needed for launch. [Callback file](template/callback.py) is your sandbox. By putting these two files and your desired font into a directory, you create valid project.

## Font
Fonts used need to be fixed width. Place `*.ttf` file in your project directory. Settings define `font_name` and `font_size`.
