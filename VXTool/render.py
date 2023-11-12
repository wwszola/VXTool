from pygame import SRCALPHA, Surface
from pygame._sdl2 import Renderer, Texture

from .core import Color, Dot, Rect
from .font import FontBank


def generate_dot_tex(dot: Dot, font_bank: FontBank, renderer: Renderer):
    font = font_bank.get(dot.font_name)

    face = font.render(dot.letter, False, dot.color)
    face.set_alpha(dot.color.a)

    size = face.get_size()
    render = Surface(size, SRCALPHA, 32)
    backcolor = dot.backcolor
    if not dot.backcolor:
        backcolor = Color(0, 0, 0, 0)
    render.fill(backcolor)

    render.blit(face, (0, 0))
    return Texture.from_surface(renderer, render)


class Canvas:
    def __init__(
        self,
        shape: tuple[int, int],
        full_res: tuple[int, int],
        backcolor: Color,
        renderer: Renderer,
    ):
        self.shape: tuple[int, int] = shape
        self.full_res: tuple[int, int] = full_res
        self.backcolor: Color = backcolor
        self.renderer = renderer

        self.block_size = full_res[0] // shape[0], full_res[1] // shape[1]
        self.render_tex = Texture(renderer, full_res, 32, target=True)

    def block_rect(self, pos: tuple[int, int]):
        return Rect(
            (pos[0] * self.block_size[0], pos[1] * self.block_size[1]), self.block_size
        )

    def clear(self):
        self.renderer.target = self.render_tex
        self.renderer.draw_color = self.backcolor
        self.renderer.clear()

    def render_blocks(self, blocks: list[tuple[Texture, Rect]]):
        self.renderer.target = self.render_tex
        for render, rect in blocks:
            self.renderer.blit(render, rect)
