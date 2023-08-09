# text_render 
## Workflow tool for rendering text-based, animated grid.
#### Might be actually a valid idea
____

`py text_render.py template`

[Template directory](template) presents minimal example of what's going on in here. Its [settings file](template/settings.json) contains all settings needed for launch. [Callback file](template/callback.py) is your sandbox. By putting these two files and your desired font into a directory, you create valid project.

#### Based on PyGame. Recording uses system call `ffmpeg` for stitching frames into video, but it's not needed for rendering.

Buffer.advance

drawing 

Now: 
Main spawns App, which spawns TextRender and Callback
App gathers events and sends it to Callback
Dots sit on Callback
Buffers(collection of dots) are sent into TextRender draw

After:
TextRender has internal StaticBuffer. 
Callback submits a diff to the queue, TextRender applies the diff and renders next surface when needed.
App gathers events every real frame, while displaying last available TextRender surface
Callback chooses to wait or not for new InputFrame.
TextRender reads the fontname from settings
Main spawns App and Callback
KeyState sitting on App. Callback accessing 

Mouse
screen_to_grid

Profile:
- dot and buffer operations

TODO:
- logging, test and measure performance
- allow for adding multiple widgets
- document and test sync variants
- handle mouse events
TODO:
- Position as (pygame.math.Vector2)
- Loading png tilesets
- Code:
- - explain exceptions instead of `pass`
- - Iterable instead of Iterator ??
- Interface:
- - pause/play/reload
- __Multiprocessing__
- - async mode (?): TextRender.draw queues immediate rendering
- - what scales worse, callback calculations or rendering
- Live music performance:
- - spectral analysis
- - midi input 