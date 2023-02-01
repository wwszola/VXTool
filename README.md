# text_render 
## Workflow tool for rendering text-based, animated grid.
#### Might be actually a valid idea
____

`py text_render.py template`

[Template directory](template) presents minimal example of what's going on in here. Its [settings file](template/settings.json) contains all settings needed for launch. [Callback file](template/callback.py) is your sandbox. By putting these two files and your desired font into a directory, you create valid project.

#### Based on PyGame. Recording uses system call `ffmpeg` for stitching frames into video, but it's not needed for rendering.

RED, GREEN, BLUE - (0 - 255)
(255, 255, 255) = WHITE

TODO:
- Position as (pygame.math.Vector2)
- Color as (pygame.color.Color)
- - Transparency
- Code:
- - explain exceptions instead of `pass`
- - Iterable instead of Iterator ??
- 
- __Buffer transformations__:
- - Buffer.dot_seq is a generator
- - map Vector2 functions on a dot_seq ->? multiprocessing
- __Multiprocessing__
- - separate processes for _app, _callback
- - async mode (?): TextRender.draw queues immediate rendering
- - what scales worse, callback calculations or rendering
- Live music performance:
- - spectral analysis
- - midi input 