from queue import Empty as QueueEmpty
from queue import Full as QueueFull
from multiprocessing import Queue

import pygame
from pygame.font import Font
from pygame.time import Clock
from pygame.image import save
from pygame.event import Event, event_name
from pygame import Rect

from pygame import QUIT, KEYDOWN, KEYUP
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame import KMOD_CTRL

from .render import TextRender, RENDER_MSG
from .core import Color

class PickableEvent:
    def __init__(self, type: int, attrs: dict = {}):
        self.type = type
        self.attrs = attrs
        self.attrs['type_name'] = event_name(self.type)
        if "window" in self.attrs:
            del self.attrs["window"]

    def __str__(self) -> str:
        return str(self.attrs)

    @staticmethod
    def cast_from(event: Event):
        return PickableEvent(event.type, event.__dict__)

    def cast(self):
        return Event(self.type, self.attrs)

    def __getstate__(self):
        return (self.type, self.attrs)
    
    def __setstate__(self, state):
        self.type = state[0]
        self.attrs = state[1]

    @property
    def type_name(self):
        return self.attrs['type_name']

def _font_preload(project_dir, font_info):
    fonts = {}
    fonts_info = {}
    for name, data in font_info.items():
        path = data[0]
        sizes = data[1:]
        try:
            for size in sizes:
                font = Font(project_dir / path, size)
                fonts[name, size] = font
                fonts_info[name, size] = {
                    "size": font.size('█')
                }
        except FileNotFoundError as e:
            print(e)
    return fonts, fonts_info

def _app(_SETTINGS: dict):
    print(f"APP settings: {_SETTINGS['APP']}")
    project_dir = _SETTINGS['USER']['project_dir']
    out_dir = _SETTINGS['USER']['out_dir']

    pygame.init()
    render_size = _SETTINGS['APP']['render_size']
    
    screen = pygame.display.set_mode(render_size, vsync=0, flags=pygame.SCALED)
    window = pygame._sdl2.Window.from_display_module()
    renderer = pygame._sdl2.Renderer.from_window(window)
    backcolor = Color(_SETTINGS["APP"]["backcolor"])

    pygame.font.init()
    fonts, fonts_info = _font_preload(project_dir, _SETTINGS['APP']['preload_fonts'])

    # hiding the cursor
    pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

    record = _SETTINGS['APP'].get('record', None)
    quit = _SETTINGS['APP'].get('quit', None)
    real_time = _SETTINGS['APP'].get('real_time', False)

    widgets = {}
    widgets_info = {}
    for name, attrs in _SETTINGS['WIDGETS'].items():
        widget = TextRender(**attrs, _font_bank = fonts, renderer = renderer)
        inv_scale = (widget.shape[0]/widget.full_res[0],
                 widget.shape[1]/widget.full_res[1])
        inv_translation = ((render_size[0]-widget.full_res[0])//2,
                     (render_size[1]-widget.full_res[1])//2)
        info = {
            'inv_scale': inv_scale,
            'inv_translation': inv_translation,
            'shape': widget.shape, 
            'render_q': widget._render_q
        }
        widgets[name] = widget
        widgets_info[name] = info

    event_out_q = Queue()
    callback = _SETTINGS['APP']['_callback'](
        widgets_info, fonts_info, _SETTINGS['USER'], event_out_q
    )
    callback.start()

    running = True
    clock = Clock()
    clock.tick(_SETTINGS['APP']['FPS'])
    frame = 0
    while running:
        running = not pygame.event.peek(QUIT)
        
        key_events = pygame.event.get((KEYDOWN, KEYUP))
        mouse_events = pygame.event.get((MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION))
        captured = filter(lambda event: bool(event.mod & KMOD_CTRL), key_events)
        for event in captured:
            match (event.key):
                case pygame.K_q:
                    running = False
                case pygame.K_s:
                    save(screen, out_dir / f'frame_{frame:0>5}.png')
                case pygame.K_r:
                    record = (frame, 999999)

        try:
            event_out_q.put(
                [PickableEvent.cast_from(event) for event in key_events + mouse_events], 
                block = real_time, 
                timeout = 1.0
            )
        except QueueFull:
            pass

        blits = []
        for widget in widgets.values():
            block = widget.frames_rendered_count == 0 or not real_time
            flags = RENDER_MSG.CONTINUE
            try:
                while flags & RENDER_MSG.CONTINUE:
                    flags = widget._render_next(block=block)
                    rect = Rect((0, 0), widget.full_res)
                    rect.center = (render_size[0]//2, render_size[1]//2)
                    renderer.target = None
                    renderer.draw_color = backcolor
                    renderer.clear()
                    renderer.blit(widget.screen, rect)
                    if flags & RENDER_MSG.STOP:
                        running = False
            except QueueEmpty:
                pass
        
        renderer.present()

        should_record = record and record[0] <= frame < record[1] 
        should_record = should_record and (real_time or (not real_time and blits))
        if should_record:
            save(screen, out_dir / f'frame_{frame:0>5}.png')

        if quit and frame >= quit:
            running = False
        
        frame += 1
        last_delta = clock.tick(_SETTINGS['APP']['FPS'])
        real_fps = 1000/last_delta
        pygame.display.set_caption(f'{real_fps:.2}')


    callback.running = False
    # event_out_q.close()
    event_out_q.cancel_join_thread()
    callback.join()
    
    pygame.quit()