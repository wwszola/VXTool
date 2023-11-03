from multiprocessing import Queue
from enum import Flag, auto
from queue import Empty as QueueEmpty

from pygame import Surface
from pygame import SRCALPHA

from pygame._sdl2 import Renderer, Texture

from .core import Color, Dot
from .font import FontBank

class RENDER_MSG(Flag):
    NO_CLEAR = auto() # Doesn't clear the screen before drawing content of the entry
    NO_CHANGE = auto() # "I don't include any content into the entry"
    CONTINUE = auto() # Process next entry immediately after this one
    SET_BLOCK_SIZE = auto() # Resizes surface to match new dot size
    REGISTER_DOTS = auto() # Register dots in _hash_to_dot dictionary
    STOP = auto()
    DEFAULT = auto()
    PROCEDURE = NO_CHANGE | CONTINUE

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

    def process_queue(self):
        try:
            while True:
                dot, hash_value = self._new_dots_q.get()
                self.register(dot, hash_value)
        except QueueEmpty:
            pass
    
    def get_render(self, hash_value: int) -> Texture:
        if hash_value not in self._hash_to_dot:
            raise KeyError(f"No dot attributed with hash value {hash_value} has been registered yet")
        if hash_value not in self._cached_renders:
            dot = self._hash_to_dot(hash_value)
            render = self._render(dot)
            self._cached_renders[hash_value] = render
        return self._cached_renders[hash_value]

    def _render(self, dot: Dot):
        font = self._font_bank.get(dot.font_name)

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
            return
        plain_dot = dot.variant(Dot) if dot.__class__ != Dot else dot
        self._new_dots_q.put((plain_dot, hash_value))
        self._registered_hashes.add(hash_value)
