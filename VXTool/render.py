from multiprocessing import Queue
from queue import Empty as QueueEmpty

from pygame import Surface
from pygame import SRCALPHA

from pygame._sdl2 import Renderer, Texture

from .core import Color, Dot
from .font import FontBank

class DotRenderer:
    def __init__(self, font_bank: FontBank, renderer: Renderer):
        self.font_bank: FontBank = font_bank
        self.renderer: Renderer = renderer

    def render(self, dot: Dot):
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

class RenderStore:
    def __init__(self):
        self._hash_to_dot: dict[int, Dot] = dict()
        self._cached_renders: dict[int, Texture] = dict()

        self._new_dots_q: Queue = Queue()

    def register(self, hash_value: int, dot: Dot):
        plain_dot = dot.variant(Dot) if dot.__class__ != Dot else dot
        self._hash_to_dot[hash_value] = plain_dot

    def is_registered(self, hash_value: int):
        return hash_value in self._hash_to_dot

    def retrieve(self, hash_value: int) -> Dot:
        return self._hash_to_dot[hash_value]

    def process(self, dot_renderer: DotRenderer):
        try:
            while True:
                hash_value, dot = self._new_dots_q.get(False)
                self.set(hash_value, dot_renderer.render(dot))            
        except QueueEmpty:
            pass

    def set(self, hash_value: int, render: Texture):
        self._cached_renders[hash_value] = render

    def get(self, hash_value: int) -> Texture:
        return self._cached_renders[hash_value]

class RenderStoreProxy:
    def __init__(self, render_store: RenderStore):
        self._registered_hashes: set[int] = set()
        self._new_dots_q: Queue = render_store._new_dots_q

    def is_registered(self, hash_value: int):
        return hash_value in self._registered_hashes

    def register(self, hash_value: int, dot: Dot):
        plain_dot = dot.variant(Dot) if dot.__class__ != Dot else dot
        self._new_dots_q.put((hash_value, plain_dot))
        self._registered_hashes.add(hash_value)
