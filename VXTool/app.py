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
from .project import get_out_dir
from .font import FontBank

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

def _app(callback, config, fonts_info):
    project_dir = config['project_dir']
    out_dir = get_out_dir(config)

    pygame.init()
    render_size = config['render_size']
    
    screen = pygame.display.set_mode(render_size, vsync=0, flags=pygame.SCALED)
    window = pygame._sdl2.Window.from_display_module()
    renderer = pygame._sdl2.Renderer.from_window(window)
    backcolor = Color(config["backcolor"])

    font_bank = FontBank()
    font_bank.load_all(fonts_info)

    # hiding the cursor
    pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

    record = config["record"]
    quit = config["quit"]
    real_time = config["real_time"]

    widget = TextRender(
        shape = config["shape"],
        full_res = config["full_res"],
        backcolor = config["backcolor"],
        _font_bank = font_bank,
        renderer = renderer
    )
    widget_rect = Rect((0, 0), widget.full_res)
    widget_rect.center = (render_size[0]//2, render_size[1]//2)
                
    inv_scale = (widget.shape[0]/widget.full_res[0],
                widget.shape[1]/widget.full_res[1])
    inv_translation = ((render_size[0]-widget.full_res[0])//2,
                    (render_size[1]-widget.full_res[1])//2)
    info = {
        'inv_scale': inv_scale,
        'inv_translation': inv_translation,
        'render_q': widget._render_q
    }

    event_out_q = Queue()
    callback_cls = callback.Callback
    callback_process = callback_cls(
        info, config, event_out_q
    )
    callback_process.start()

    FPS = config["FPS"]
    running = True
    clock = Clock()
    clock.tick(FPS)
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

        block = widget.frames_rendered_count == 0 or not real_time
        flags = RENDER_MSG.CONTINUE
        try:
            while flags & RENDER_MSG.CONTINUE:
                flags = widget._render_next(block=block)
                renderer.target = None
                renderer.draw_color = backcolor
                renderer.clear()
                renderer.blit(widget.screen, widget_rect)
                if flags & RENDER_MSG.STOP:
                    running = False
        except QueueEmpty:
            pass
        
        renderer.present()

        should_record = record and record[0] <= frame < record[1] 
        if should_record:
            save(screen, out_dir / f'frame_{frame:0>5}.png')

        if quit and frame >= quit:
            running = False
        
        frame += 1
        last_delta = clock.tick(FPS)
        real_fps = 1000/last_delta
        pygame.display.set_caption(f'{real_fps:.2}')


    callback_process.running = False
    # event_out_q.close()
    event_out_q.cancel_join_thread()
    callback_process.join()
    
    pygame.quit()