from queue import Empty as QueueEmpty
from multiprocessing import Queue
from pathlib import Path

import pygame
from pygame.time import Clock
from pygame.event import Event, event_name
from pygame import Rect

from pygame import QUIT, KEYDOWN, KEYUP
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame import KMOD_CTRL

from pygame._sdl2 import Window, Renderer, Texture

from .render import DotRenderer, RENDER_MSG
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

class App:
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
        
        self.running = False
        self.frame: int = -1

    def __del__(self):
        if pygame.get_init():
            pygame.quit()

    def init_render_context(self, font_bank: FontBank):
        self._window: Window = Window(resizable = False)
        self._renderer: Renderer = Renderer(self._window, target_texture = True)
        self._render_tex: Texture = None

        self._render_q: Queue = Queue()
        self._dot_renderer: DotRenderer = DotRenderer(font_bank, self._renderer)

    def init_event_context(self):
        self._events: list = list()
        self._event_q: Queue = Queue()

    def apply_config(self, config: dict):
        render_size = config.get("render_size", None)
        if render_size is None:
            raise ValueError(f"Invalid 'render_size' key in config:\n{config}")
        
        self._window.size = render_size
        self._render_tex = Texture(self._renderer, render_size, 32, target = True)
        
        self._config: dict = config

    def _get_screenshot_filename(self, _frame: int | None = None):
        if _frame is None:
            _frame = self.frame
        return self._config["out_dir"] / f"frame_{_frame:0>5}.png"
    
    def _screenshot(self, filename: str | Path):
        filename = str(filename)
        raise NotImplementedError("Saving a screen using sdl2 renderer")

    def _block_rect(self, pos):
        shape = self._config["shape"]
        full_res = self._config["full_res"]
        block_size = full_res[0] // shape[0], full_res[1] // shape[1]
        return Rect((pos[0]*block_size[0], pos[1]*block_size[1]), block_size)
    
    def _process_render_entry(self, entry):
        flags = entry[0]
        args = list(entry[1:])

        if not flags & RENDER_MSG.NO_CHANGE:
            data = args.pop(0)
            data_it = iter(data)
            blits = []
            while True:
                try:
                    pos = next(data_it)
                    rect = self.block_rect(pos)
                    length = next(data_it)
                    for _ in range(length):
                        _hash = next(data_it)
                        render = self._dot_renderer.get_render(_hash)
                        blits.append((render, rect))
                except StopIteration:
                    break        

            if not flags & RENDER_MSG.NO_CLEAR:
                self.renderer.draw_color = self.backcolor
                self.renderer.clear()
            for render, rect in blits:
                self.renderer.blit(render, rect)
        
        return flags
            
    def _render_next_frame(self, block: bool = True, timeout: float | None = None):
        self.renderer.target = self._render_tex
        
        real_time = self._config.get("real_time", False)
        block = self.frame == 0 or not real_time
        flags = RENDER_MSG.CONTINUE
        try:
            while flags & RENDER_MSG.CONTINUE:
                entry = self._render_q.get(block, timeout)
                flags = self._process_render_entry(entry)
                if flags & RENDER_MSG.STOP:
                    self.running = False
        except QueueEmpty:
            pass
        
        self.frame += 1

    def _process_events(self):
        self.running = not pygame.event.peek(QUIT)

        key_events = pygame.event.get((KEYDOWN, KEYUP))
        mouse_events = pygame.event.get((MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION))
        self._events.clear()
        self._events.extend(key_events + mouse_events)

        captured = list(filter(lambda event: bool(event.mod & KMOD_CTRL), key_events))
        self._process_shortcuts(captured)

        self._event_q.put(
            [PickableEvent.cast_from(event) for event in self._events], 
            block = self._config["real_time"],
            timeout = 1.0
        )

    def _process_shortcuts(self, captured: list):
        for event in captured:
            match (event.key):
                case pygame.K_q:
                    self.running = False
                case pygame.K_s:
                    self._screenshot(self._get_screenshot_filename(self.frame - 1))

    def _main_loop(self):
        self.running = True
        self.frame = 0

        FPS = self._config.get("FPS", None)
        record = self._config.get("record", (0, 0))
        quit = self._config.get("quit", -1)

        clock = Clock()
        clock.tick()
        while self.running:
            self._window.title = f"{clock.get_fps():.2}"

            self._process_events()
            self._dot_renderer.process_queue()
            self._render_next_frame()
            self._renderer.target = None
            self._renderer.draw_color = self._config["backcolor"]
            self._renderer.clear()
            self.renderer.blit(self._render_tex, None)
                    
            self.renderer.present()

            should_record = record[0] <= self.frame < record[1] 
            if should_record:
                self._screenshot(self._get_screenshot_filename())
            
            if quit >= self.frame:
                self.running = False
            
            self.frame += 1
            clock.tick(FPS)
