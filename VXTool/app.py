from queue import Empty as QueueEmpty
from multiprocessing import Queue
from pathlib import Path
from enum import Enum, auto
from types import ModuleType

import pygame
from pygame.time import Clock
from pygame.event import Event, event_name
from pygame import Surface, Rect

from pygame import QUIT, KEYDOWN, KEYUP
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame import KMOD_CTRL

from pygame._sdl2 import Window, Renderer, Texture

from .project import ProjectContext
from .render import Canvas, generate_dot_tex
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

class ACTION_MSG(Enum):
    REGISTER_DOTS = auto()
    RENDER = auto()
    CLEAR = auto()
    UPDATE = auto()
    QUIT = auto()

class App:
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
        
        self._window: Window = Window(resizable = True)
        self._renderer: Renderer = Renderer(self._window, target_texture=True)
        self._cached_renders: dict[int, Texture] = dict()
        self._font_bank = FontBank()

        self._msg_q: Queue[ACTION_MSG] = Queue()
        self._data_q: Queue = Queue()

        self._events: list = list()
        self._event_q: Queue = Queue()

        self.running = False
        self.frame: int = -1

    def __del__(self):
        if pygame.get_init():
            pygame.quit()

    def run(self, project: ProjectContext):
        self._current_project = project
        self._canvas = Canvas(project.config["shape"], project.config["full_res"], project.config["backcolor"], self._renderer)
        
        render_size = project.config["render_size"]
        self._window.size = render_size
        self._renderer.logical_size = render_size

        for font_info in project.fonts_info:
            self._font_bank.load(font_info)

        self._callback_process = project.callback_module.Callback(self._msg_q, self._data_q, self._event_q)
        self._callback_process.start()

        self._main_loop()
        self.stop()

    def _get_screenshot_filename(self, _frame: int | None = None):
        if _frame is None:
            _frame = self.frame
        return self._current_project.config["out_dir"] / f"frame_{_frame:0>5}.png"
    
    def _screenshot(self, filename: str | Path):
        filename = str(filename)
        screen: Surface = self._renderer.to_surface()
        pygame.image.save(screen, filename)

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
            block = True
        )

    def _process_shortcuts(self, captured: list):
        for event in captured:
            match (event.key):
                case pygame.K_q:
                    self.running = False
                case pygame.K_s:
                    self._screenshot(self._get_screenshot_filename(self.frame - 1))

    def stop(self):
        if self._callback_process:
            self._callback_process.running = False
            self._callback_process.join()

    def _register_dots(self):
        new_dots = self._data_q.get()
        for hash_value, dot in new_dots:
            tex = generate_dot_tex(dot, self._font_bank, self._renderer) 
            self._cached_renders[hash_value] = tex
        
    def _get_blits(self):
        blits = []
        try:
            data = self._data_q.get()
            data_it = iter(data)
            blits = []
            while True:
                pos = next(data_it)
                rect = self._canvas.block_rect(pos)
                length = next(data_it)
                for _ in range(length):
                    hash_value = next(data_it)
                    render = self._cached_renders.get(hash_value)
                    blits.append((render, rect))
        except (QueueEmpty, StopIteration):
            pass
        return blits
    
    def _render(self):
        blits = self._get_blits()
        self._canvas.render_blocks(blits)

    def _clear(self):
        self._canvas.clear()

    def _canvas_rect(self):
        render_size = self._current_project.config["render_size"]
        full_res = self._canvas.full_res
        canvas_rect = Rect((0, 0), full_res)
        canvas_rect.center = render_size[0]//2, render_size[1]//2
        return canvas_rect

    def _update_screen(self):
        self._renderer.target = None
        self._renderer.draw_color = self._current_project.config["backcolor"]
        self._renderer.clear()
        self._renderer.blit(self._canvas.render_tex, self._canvas_rect())
        self._renderer.present()

    def _action_loop(self):
        while True:
            action: ACTION_MSG = self._msg_q.get()
            match action:
                case ACTION_MSG.REGISTER_DOTS:
                    self._register_dots()
                case ACTION_MSG.RENDER:
                    self._render()
                case ACTION_MSG.CLEAR:
                    self._clear()
                case ACTION_MSG.UPDATE:
                    self._update_screen()
                    break
                case ACTION_MSG.QUIT:
                    self.running = False
                    break

    def _main_loop(self):
        self.running = True
        self.frame = 0

        FPS = self._current_project.config["FPS"]
        record = self._current_project.config["record"]
        quit = self._current_project.config["quit"]

        clock = Clock()
        clock.tick()
        while self.running:
            self._window.title = f"{clock.get_fps():.2}"
            self._process_events()

            self._action_loop()

            should_record = record[0] <= self.frame < record[1] 
            if should_record:
                self._screenshot(self._get_screenshot_filename())

            if quit >= 0 and self.frame >= quit:
                self.running = False

            self.frame += 1
            clock.tick(FPS)

