# text_render 
## Workflow tool for rendering text-based, animated grid.
#### Might be actually a valid idea
____

`py text_render.py template`

[Template directory](template) presents minimal example of what's going on in here. Its [settings file](template/settings.json) contains all settings needed for launch. [Callback file](template/callback.py) is your sandbox. By putting these two files and your desired font into a directory, you create valid project.

#### Based on PyGame. Recording uses system call `ffmpeg` for stitching frames into video, but it's not needed for rendering.