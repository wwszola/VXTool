from dataclasses import dataclass, field
from multiprocessing import Queue
from enum import Flag, auto

from pygame import Surface, Rect
from pygame.font import Font
from pygame.transform import scale
from pygame import SRCALPHA

from .core import Color, BLACK, Dot, Buffer, BoundBuffer

class RENDER_MSG(Flag):
    CLEAR = auto()
    NO_CHANGE = auto()
    CONTINUE = auto()
    SET_BLOCK_SIZE = auto()
    REGISTER_DOTS = auto()
    DEFAULT = CLEAR
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

    _last_state: BoundBuffer = field(init = False)
    _render_q: Queue = field(init = False)
    frames_rendered_count: int = field(init = False, default = 0)

    def __post_init__(self):
        if self.block_size:
            self.resize_screen()
        self._last_state = BoundBuffer(region = self.grid_rect)
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
        self.cached_renders['_EMPTY'] = empty_block

    def block_rect(self, pos: tuple[int, int]) -> Rect:
        return Rect(
            (pos[0] * self.block_size[0], pos[1] * self.block_size[1]),
            self.block_size
        )

    @property
    def grid_rect(self) -> Rect:
        return Rect((0, 0), self.shape)

    def get_dot_size(self, dot: Dot) -> Font:
        return self._font_bank[dot.font_family][dot.font_size].size(dot.letter)

    def _gen_dot_render(self, dot: Dot) -> Surface:
        block_render = Surface(self.block_size, SRCALPHA)

        backcolor = dot.backcolor 
        if not dot.clear and not dot.backcolor:
            backcolor = (0, 0, 0, 0)
        if dot.clear and not dot.backcolor:
            backcolor = self.backcolor
        block_render.fill(backcolor)            

        font = self._font_bank[dot.font_family][dot.font_size]

        dot_render = font.render(dot.letter, False, dot.color)
        dot_render = dot_render.convert_alpha(block_render)
        dot_render.set_alpha(dot.color.a)

        rect = dot_render.get_rect(center = block_render.get_rect().center)
        block_render.blit(dot_render, rect)
        
        block_render = block_render.convert_alpha()
        return block_render

    def _register_dot(self, dot: Dot):
        _hash = hash(dot)
        self._hash_to_dot.setdefault(_hash, dot)

    def _render_next(self, block = True, timeout: float = None):
        entry = self._render_q.get(block, timeout)
        # print(f"TEXTRENDER ENTRY: {entry}")
        flags = entry[0]
        args = list(entry[1:])

        if flags & RENDER_MSG.SET_BLOCK_SIZE:
            dot = args.pop(0)
            block_size = self.get_dot_size(dot)
            self.block_size = block_size
            self.resize_screen()

        if flags & RENDER_MSG.REGISTER_DOTS:
            new_dots = args.pop(0)
            for _hash, dot in new_dots:
                self._hash_to_dot[_hash] = dot

        if not flags & RENDER_MSG.NO_CHANGE:
            # buffer = BoundBuffer(region=self.grid_rect)
            # buffer.merge(entry[-1])
            # diff, clear_mask = self._last_state.diff(buffer)
            # # print('RENDER DIFF: ', diff, clear_mask)
            
            # if diff.is_empty() and len(clear_mask) == 0:
            #     return None, flags
            
            # all_blits = self._all_blits(diff, clear_mask)
            # # print('ALL BLITS: ', all_blits)
            # self.screen.blits(all_blits)
            # self._last_state = buffer

            data = args.pop(0)
            data_it = iter(data)
            blits = []
            while True:
                try:
                    pos = next(data_it)
                    length = next(data_it)
                    for _ in range(length):
                        _hash = next(data_it)
                    if _hash not in self.cached_renders:
                        dot = self._hash_to_dot[_hash]
                        self.cached_renders[_hash] = self._gen_dot_render(dot)
                    rect = self.block_rect(pos)
                    blits.append((self.cached_renders[_hash], rect))
                except StopIteration:
                    break        

            if flags & RENDER_MSG.CLEAR:
                self.screen.fill(self.backcolor)
            self.screen.blits(blits)

        self.frames_rendered_count += 1
        return scale(self.screen, self.full_res), flags

    def _all_blits(self, diff: Buffer, clear_mask: set[tuple[int, int]]):
        blits = []
        
        empty_dot = self.cached_renders["_EMPTY"]
        for pos in clear_mask:
            design_block = self.block_rect(pos)
            blits.append((empty_dot, design_block))
        
        for pos, dots in diff._container.items():
            design_block = self.block_rect(pos)
            for dot in dots:
                dot_render = self._get_render(dot)
                blits.append((dot_render, design_block))
        return blits        

    def clear(self, region: Rect = None):
        if not region:
            region = self.grid_rect
        region = Rect(
            region.left * self.block_size[0],
            region.top * self.block_size[1],
            region.width * self.block_size[0],
            region.height * self.block_size[1]
        )
        self.screen.fill(self.backcolor, region)     
