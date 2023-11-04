from multiprocessing import Queue
from enum import Flag, auto
from queue import Empty as QueueEmpty

from pygame import Surface
from pygame import SRCALPHA

from pygame._sdl2 import Renderer, Texture

from .core import Color, Dot
from .font import FontBank

class FrameInfo:
    def __init__(self, count: int, new_dots: int = 0, clear_screen: bool = True, quit_after: bool = False):
        self.count: int = count
        self.new_dots: int = new_dots
        self.clear_screen: bool = clear_screen
        self.quit_after: bool = quit_after

class DotRenderer:
    def __init__(self, font_bank: FontBank, renderer: Renderer):
        self.font_bank: FontBank = font_bank
        self.renderer: Renderer = renderer

        self._hash_to_dot: dict[int, Dot] = dict()
        self._cached_renders: dict[int, Texture] = dict()

        self._new_dots_q: Queue = Queue()

    def register(self, dot: Dot, hash_value: int):
        plain_dot = dot.variant(Dot) if dot.__class__ != Dot else dot
        self._hash_to_dot[hash_value] = plain_dot

    def process_queue(self, count: int = 1):
        try:
            for _ in range(count):
                dot, hash_value = self._new_dots_q.get()
                self.register(dot, hash_value)
        except QueueEmpty:
            pass
    
    def get_render(self, hash_value: int) -> Texture:
        if hash_value not in self._hash_to_dot:
            raise KeyError(f"No dot attributed with hash value {hash_value} has been registered yet")
        if hash_value not in self._cached_renders:
            dot = self._hash_to_dot[hash_value]
            render = self._render(dot)
            self._cached_renders[hash_value] = render
        return self._cached_renders[hash_value]

    def _render(self, dot: Dot):
        font = self.font_bank.get(dot.font_name)

        face = font.render(dot.letter, False, dot.color)
        face.set_alpha(dot.color.a)

        size = face.get_size()
        render = Surface(size, SRCALPHA, 32)
        backcolor = dot.backcolor 
        if not dot.backcolor:
            backcolor = Color(0, 0, 0, 0)
        render.fill(backcolor)

        render.blit(face, (0, 0))
        return Texture.from_surface(self.renderer, render)

class DotRendererProxy:
    def __init__(self, dot_renderer: DotRenderer):
        self._registered_hashes: set[int] = set()
        self._new_dots_q: Queue = dot_renderer._new_dots_q

    def register(self, dot: Dot, hash_value: int):
        if hash_value in self._registered_hashes:
            return False
        plain_dot = dot.variant(Dot) if dot.__class__ != Dot else dot
        self._new_dots_q.put((plain_dot, hash_value))
        self._registered_hashes.add(hash_value)
        return True