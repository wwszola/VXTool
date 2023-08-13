from queue import Empty as QueueEmpty
from queue import Full as QueueFull
from multiprocessing import Queue

import pygame
from pygame.font import Font
from pygame.time import Clock
from pygame.image import save
from pygame.event import Event, event_name

from pygame import QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame import KMOD_CTRL

from .render import TextRender, RENDER_MSG

class PickableEvent:
    def __init__(self, type: int, attrs: dict = {}):
        self.type = type
        self.attrs = attrs
        self.attrs['type_name'] = event_name(self.type)

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
    for name, data in font_info.items():
        path = data[0]
        family = fonts[name] = {}
        try: 
            for size in data[1:]:
                font = Font(project_dir / path, size)
                family[size] = font            
        except FileNotFoundError as e:
            print(e.msg)
    return fonts

def _app(_SETTINGS: dict):
    print(f"APP settings: {_SETTINGS['APP']}")
    project_dir = _SETTINGS['USER']['project_dir']
    out_dir = _SETTINGS['USER']['out_dir']

    pygame.init()
    render_size = _SETTINGS['APP']['render_size']
    screen = pygame.display.set_mode(render_size)

    pygame.font.init()
    fonts = _font_preload(project_dir, _SETTINGS['APP']['preload_fonts'])

    record = _SETTINGS['APP'].get('record', None)
    quit = _SETTINGS['APP'].get('quit', None)
    real_time = _SETTINGS['APP'].get('real_time', False)

    widgets = {}
    widgets_info = {}
    for name, attrs in _SETTINGS['WIDGETS'].items():
        widget = TextRender(**attrs, _font_bank = fonts)
        info = {'shape': widget.shape, 'render_q': widget._render_q}
        widgets[name] = widget
        widgets_info[name] = info

    event_out_q = Queue()
    callback = _SETTINGS['APP']['_callback'](widgets_info, _SETTINGS['USER'], event_out_q)
    callback.start()

    running = True
    clock = Clock()
    frame = 0
    while running:
        running = not pygame.event.peek(QUIT)
        
        keydowns = pygame.event.get(KEYDOWN)
        captured = filter(lambda event: bool(event.mod & KMOD_CTRL), keydowns)
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
                [PickableEvent.cast_from(event) for event in keydowns], 
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
                    surface, flags = widget._render_next(block=block)
                    if surface is not None:
                        rect = surface.get_rect(center = screen.get_rect().center)
                        blits.append((surface, rect))
            except QueueEmpty:
                pass
        # print(f"WDIGET FRAMES NO. {widget.frames_rendered_count}")
        # print(f"APP FRAMES: {frame}")
        # print("SCREEN BLITS:", blits)
        # screen.fill(_SETTINGS['APP']['backcolor'])
        if blits:
            screen.blits(blits)
            pygame.display.update()

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