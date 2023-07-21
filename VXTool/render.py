from dataclasses import dataclass, field

from pygame import Surface, Rect
from pygame.font import Font
from pygame.transform import scale
from pygame import SRCALPHA

from .core import Color, BLACK, Dot, Buffer

@dataclass
class TextRender:
    shape: tuple[int, int]
    full_res: tuple[int, int]
    block_size: tuple[int, int] = None

    backcolor: Color = BLACK

    _font_bank: dict[Font] = field(default_factory = dict)
    
    cached_renders: dict[Dot, Surface] = field(default_factory = dict, kw_only = True)
    _screen: Surface = field(init = False)

    def __post_init__(self):
        if self.block_size:
            self.resize_screen()

    @property
    def full_size(self) -> tuple[int, int]:
        return (self.shape[0] * self.block_size[0], self.shape[1] * self.block_size[1])

    def resize_screen(self):
        print(f'Block size: {self.block_size} Full size: {self.full_size}')
        self.screen = Surface(self.full_size, SRCALPHA)
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

    def _get_render(self, dot: Dot) -> Surface:
        dot_render = self.cached_renders.get(dot, None)
        if not dot_render:
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
            self.cached_renders[dot] = block_render
        
        return self.cached_renders[dot]

    def draw(self, buffer: Buffer):
        blits = []
        for pos, dots in buffer._container.items():
            design_block = self.block_rect(pos)
            for dot in dots:
                dot_render = self._get_render(dot)
                # rect = dot_render.get_rect(center = design_block.center)
                blits.append((dot_render, design_block))
        self.screen.blits(blits)
    
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

    def img(self) -> Surface:
        return scale(self.screen, self.full_res)       
