# text_render 
## Workflow tool for rendering text-based, animated grid.
#### Might be actually a valid idea
____

`py text_render.py template`

[Template directory](template) presents minimal example of what's going on in here. Its [settings file](template/settings.json) contains all settings needed for launch. [Callback file](template/callback.py) is your sandbox. By putting these two files and your desired font into a directory, you create valid project.

#### Based on PyGame. Recording uses system call `ffmpeg` for stitching frames into video, but it's not needed for rendering.


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

TODO:
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