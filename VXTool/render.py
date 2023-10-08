from dataclasses import dataclass, field
from multiprocessing import Queue
from enum import Flag, auto

from pygame import Surface, Rect
from pygame.font import Font
from pygame import transform
from pygame import SRCALPHA

from .core import Color, BLACK, Dot, Buffer

class RENDER_MSG(Flag):
    NO_CLEAR = auto() # Doesn't clear the screen before drawing content of the entry
    NO_CHANGE = auto() # "I don't include any content into the entry"
    CONTINUE = auto() # Process next entry immediately after this one
    SET_BLOCK_SIZE = auto() # Resizes surface to match new dot size
    REGISTER_DOTS = auto() # Register dots in _hash_to_dot dictionary
    STOP = auto()
    DEFAULT = auto()
    PROCEDURE = NO_CHANGE | CONTINUE

@dataclass
class TextRender:
    shape: tuple[int, int]
    full_res: tuple[int, int]
    block_size: tuple[int, int] = None

    backcolor: Color = BLACK

    _font_bank: dict[Font] = field(default_factory = dict)
    
    cached_renders: dict[int|str, Surface] = field(default_factory = dict, kw_only = True)
    _hash_to_dot: dict[int, Dot] = field(default_factory=dict, kw_only=True)
    _screen: Surface = field(init = False, default = None)

    _render_q: Queue = field(init = False)
    frames_rendered_count: int = field(init = False, default = 0)

    def __post_init__(self):
        if self.block_size:
            self.resize_screen()
        self._render_q = Queue()

    @property
    def full_size(self) -> tuple[int, int]:
        return (self.shape[0] * self.block_size[0], self.shape[1] * self.block_size[1])

    def should_resize(self):
        return (not self.screen and self.block_size) or (self.screen and self.screen.get_size() != self.full_size)

    def resize_screen(self):
        print(f'Block size: {self.block_size} Full size: {self.full_size}')
        self.screen = Surface(self.full_size, SRCALPHA)
        self.screen.fill(self.backcolor)
        empty_block = Surface(self.block_size, SRCALPHA)
        empty_block.fill(self.backcolor)
        self.cached_renders.clear()

    def block_rect(self, pos: tuple[int, int]) -> Rect:
        return Rect(
            (pos[0] * self.block_size[0], pos[1] * self.block_size[1]),
            self.block_size
        )

    @property
    def grid_rect(self) -> Rect:
        return Rect((0, 0), self.shape)

    def get_font(self, name: str, size: int) -> Font:
        return self._font_bank[name, size]
    
    def get_dot_size(self, dot: Dot):
        return self.get_font(dot.font_family, dot.font_size).size(dot.letter)

    def _gen_dot_render(self, dot: Dot) -> Surface:
        block_render = Surface(self.block_size, SRCALPHA)
        block_rect = block_render.get_rect()

        backcolor = dot.backcolor 
        if not dot.clear and not dot.backcolor:
            backcolor = Color(0, 0, 0, 0)
        if dot.clear and not dot.backcolor:
            backcolor = self.backcolor
        block_render.fill(backcolor)

        font = self.get_font(dot.font_family, dot.font_size)

        dot_render = font.render(dot.letter, False, dot.color)
        dot_render = dot_render.convert_alpha(block_render)
        dot_render.set_alpha(dot.color.a)
        
        align = dot.align.strip().lower()
        match align:
            case 'stretch':
                dot_render = transform.scale(dot_render, block_rect.size)
                rect = block_rect
            case 'center' | _:
                rect = dot_render.get_rect(center = block_rect.center)

        block_render.blit(dot_render, rect)
        block_render = block_render.convert_alpha()
        return block_render

    def _render_next(self, block = True, timeout: float = None):
        entry = self._render_q.get(block, timeout)
        # print(f"TEXTRENDER ENTRY: {entry}")
        flags = entry[0]
        args = list(entry[1:])

        if flags & RENDER_MSG.SET_BLOCK_SIZE:
            value = args.pop(0)
            if isinstance(value, Dot):
                block_size = self.get_dot_size(value)
                self.block_size = block_size
            else:
                self.block_size = value
            self.resize_screen()

        if flags & RENDER_MSG.REGISTER_DOTS:
            new_dots = args.pop(0)
            for _hash, dot in new_dots:
                self._hash_to_dot[_hash] = dot

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
                        if _hash not in self.cached_renders:
                            dot = self._hash_to_dot[_hash]
                            self.cached_renders[_hash] = self._gen_dot_render(dot)
                        blits.append((self.cached_renders[_hash], rect))
                except StopIteration:
                    break        

            if not flags & RENDER_MSG.NO_CLEAR:
                self.screen.fill(self.backcolor)
            self.screen.blits(blits)

        if flags & RENDER_MSG.NO_CHANGE or flags & RENDER_MSG.CONTINUE:
            return None, flags

        self.frames_rendered_count += 1
        return transform.scale(self.screen, self.full_res), flags
