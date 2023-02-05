from dataclasses import dataclass, field
from itertools import chain, pairwise
from json import load
from pathlib import Path
from sys import argv, path
from typing import Iterator, Generator, Callable
from dataclasses import dataclass
from collections import OrderedDict
from math import sqrt, pi, sin, cos
from copy import copy

import pygame
from pygame import Surface, Rect
from pygame.font import Font
from pygame.transform import scale
from pygame.time import Clock
from pygame.image import save
from pygame import QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame import KMOD_CTRL

class Color(pygame.Color):
    def __hash__(self):
        return hash(tuple(self))

BLACK = Color(0, 0, 0, 255)

@dataclass(eq = True, frozen = True)
class Dot():
    pos: tuple[int, int] = field(default = None, hash = False, compare = False)
    
    letter: str = None
    color: Color = None
    backcolor: Color = field(default = None, kw_only = True)
    font: Font | None = None
    clear: bool = True

    @property
    def size(self):
        return self.font.size(self.letter)

    @property
    def rect(self) -> Rect:
        return Rect((0, 0), self.size)

    def variant(self, **kwargs):
        attrs = copy(self.__dict__)
        attrs.update(kwargs)
        return Dot(**attrs)


@dataclass()
class Buffer():
    _container: dict[tuple[int, int], list[Dot]] = field(default_factory = dict)
    
    def put(self, dot: Dot):
        local: list[Dot] = self._container.setdefault(dot.pos, [])
        if dot.clear or dot.backcolor is not None:
            local.append(dot)
        else:
            try:
                local.remove(dot)
            except ValueError:
                pass
            finally:
               local.append(dot)

    def extend(self, dots: Iterator[Dot]):
        for dot in dots:
            self.put(dot)

    def erase(self, dot: Dot):
        try:
            local = self._container[dot.pos]
            local.remove(dot)
            if len(local) == 0:
                del self._container[dot.pos]
        except (KeyError, ValueError):
            pass
    
    def erase_at(self, pos: tuple[int, int], idx: int = -1):
        try:
            local = self._container[pos]
            local.pop(idx)
            if len(local) == 0:
                del self._container[pos]
        except (KeyError, IndexError):
            pass

    def clear(self):
        self._container.clear()

    def merge(self, other):
        for dots in other._container.values():
            self.extend(dots)
        # self.extend(chain(other._container.values()))

    def edit_inp(self, pos: tuple[int, int], idx: int = -1, **kwargs):
        try:
            local = self._container[pos]
            old_dot = local.pop(idx)
            if 'pos' in list(kwargs.keys()):
                del kwargs[pos]
            new_dot = old_dot.variant(**kwargs)
            local.insert(idx, new_dot)
        except (KeyError, IndexError):
            pass
    
    def dot_seq(self) -> Generator:
        for pos, dots in self._container.items():
            yield from dots

    @staticmethod
    def from_dot_seq(dots):
        buffer = Buffer()
        buffer.extend(dots)
        return buffer

    def mask(self):
        yield from self._container.keys()

@dataclass
class TextRender:
    shape: tuple[int, int]
    full_res: tuple[int, int]
    block_size: tuple[int, int] = None

    backcolor: Color = BLACK
    
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
        self.screen = Surface(self.full_size, pygame.SRCALPHA, 32)
        empty_block = Surface(self.block_size, pygame.SRCALPHA, 32)
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

    def _get_render(self, dot: Dot) -> Surface:
        dot_render = self.cached_renders.get(dot, None)
        if not dot_render:
            block_render = Surface(self.block_size, pygame.SRCALPHA, 32)

            backcolor = dot.backcolor 
            if not dot.clear and not dot.backcolor:
                backcolor = (0, 0, 0, 0)
            if dot.clear and not dot.backcolor:
                backcolor = self.backcolor
            block_render.fill(backcolor)            

            dot_render = dot.font.render(dot.letter, False, dot.color)
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

    
def _app(_SETTINGS: dict):
    project_dir = _SETTINGS['USER']['project_dir']
    out_dir = _SETTINGS['USER']['out_dir']

    pygame.init()
    render_size = _SETTINGS['APP']['render_size']
    screen = pygame.display.set_mode(render_size)

    pygame.font.init()
    for name, data in _SETTINGS['APP']['preload_fonts'].items():
        path = data[0]
        family = _SETTINGS['USER']['fonts'][name] = {}
        try: 
            for size in data[1:]:
                font = Font(project_dir / path, size)
                family[size] = font            
        except FileNotFoundError as e:
            print(e.msg)

    design = TextRender(**_SETTINGS['TEXT_RENDER'])
    action: Generator = _SETTINGS['APP']['_callback'](design, _SETTINGS['USER'])
    running = action.send(None)

    clock = Clock()

    record = _SETTINGS['APP'].get('record', None)
    quit = _SETTINGS['APP'].get('quit', None)

    frame = 0
    while running:
        if pygame.event.get(QUIT):
            running = False
        
        captured = pygame.event.get((
            KEYDOWN, KEYUP, 
            MOUSEBUTTONDOWN, MOUSEBUTTONUP
        ), pump = True)
        
        mods = pygame.key.get_mods()
        is_ctrl_mod = bool(mods & KMOD_CTRL)
        if is_ctrl_mod:
            keydowns = filter(lambda e: e.type == KEYDOWN, captured)
            for event in keydowns:
                match (event.key):
                    case pygame.K_q:
                        running = False
                    case pygame.K_s:
                        save(screen, out_dir / f'frame_{frame:0>5}.png')
                
        result = action.send(captured)
        if not result:
            running = False

        render = design.img()
        
        screen.fill(_SETTINGS['APP']['backcolor'])
        screen.blit(
            render,
            render.get_rect(center = screen.get_rect().center))

        pygame.display.update()

        if record and record[0] <= frame < record[1]:
            save(screen, out_dir / f'frame_{frame:0>5}.png')

        if quit and frame >= quit:
            running = False
            
        frame += 1
        real_fps = 1000/clock.tick(_SETTINGS['APP']['FPS'])
        pygame.display.set_caption(f'{real_fps:.2}')

    pygame.quit()

def _main():
    project_dir: Path = Path(argv[1]) 
    out_dir = project_dir / 'out'
    print(project_dir)

    _SETTINGS = OrderedDict([
        ("USER", OrderedDict([
            ("fonts", {}),
            ("project_dir", project_dir),
            ("out_dir", out_dir)
        ]))
    ])
    settings = project_dir / 'settings.json'
    with open(settings, 'r') as file:
        data = load(file, object_pairs_hook = OrderedDict)
        data['USER'].update(_SETTINGS['USER'])
        _SETTINGS.update(data)

    if "COLORS" in _SETTINGS["USER"]:
        colors = OrderedDict()
        for color_name, rgba in _SETTINGS["USER"]["COLORS"].items():
            colors[color_name] = Color(*rgba)
        _SETTINGS["USER"]["COLORS"] = colors

    _SETTINGS['TASKS']: dict = {
        'movie': _movie_task_call
    }
    
    if len(argv) > 2 and argv[2] in _SETTINGS['TASKS'].keys():
        call = _SETTINGS['TASKS'].get(argv[2], None)
        if call: call(_SETTINGS)
        return 2

    try:
        path.append(project_dir.as_posix())
        from callback import _callback
        assert _callback
        _SETTINGS['APP']['_callback'] = _callback
    except (ImportError, AssertionError) as e:
        print(e.msg)
        return 3
    
    _app(_SETTINGS)

    for task in _SETTINGS['APP']['end_tasks']:
        call = _SETTINGS['TASKS'][task]
        if call: call(_SETTINGS)

# Tasks
def _movie_task_str(settings: dict) -> str:
    """this is ffmpeg sequence that worked for me"""
    fps = settings['APP']['FPS']
    out_dir = settings['USER']['out_dir']
    return f'ffmpeg -framerate {fps} -i ' + (out_dir / f'frame_%05d.png').as_posix() + ' -c:v libx264 -pix_fmt yuv420p -vf scale=out_color_matrix=bt709 -r 30 ' + (out_dir / 'movie.mp4').as_posix()

def _movie_task_call(settings: dict, *args):
    from os import system
    system(_movie_task_str(settings))

if __name__ == '__main__':
    _main()

# Utility functions
def words_line(text: str, pos: tuple[int, int] = (0, 0)) -> Generator:
    y = pos[1]
    for i, letter in enumerate(text):
        x = pos[0] + i
        yield (x, y), letter

def words_bound(text: str, region: Rect) -> Generator:
    pos = (0, 0)
    while len(text) > 0 and pos[1] < region.height:
        cut = region.width - pos[0]
        word = text[:cut]
        text = text[cut:]
        yield from words_line(
            word, 
            (pos[0] + region.left, pos[1] + region.top)
        )
        if pos[0] + len(word) >= region.width:
            pos = (0, pos[1] + 1)
        else:
            pos = (pos[0] + len(word), pos[1])

def scroll(text: str, window: int, start: int = 0) -> Iterator[str]:
    """yields views starting from empty view, shifts to left
    returns number of views yield

    Parameters:
    text: str
    window: int
        length of the view
    start: int = 0
        pass value < window to start from partially filled view
    """
    text = ' ' * window + text
    length = 0
    for pos in range(start, len(text) - window + 1):
        yield text[pos: pos + window]
        length += 1
    return length

def reveal(text: str, start: int = 0) -> Iterator[str]:
    d = len(text)
    for pos in range(start, d + 1):
        # yield text[0: pos] + ' ' * (d - pos)
        yield text[0: pos]
    return d

def line_seq(p1: tuple[float, float], p2: tuple[float, float], end: int = 1, snap: Callable = round) -> Generator:
    """DDA line generating algorithm"""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    step = max(abs(dx), abs(dy))
    
    if step <= 1e-16:
        yield snap(p1[0]), snap(p1[1])
    else:
        dx, dy = dx / step, dy / step
        for i in range(round(step) + end):
            x = p1[0] + i * dx
            y = p1[1] + i * dy
            yield snap(x), snap(y)

def grid_seq(shape: tuple[int, int], origin: tuple[int, int] = (0, 0)) -> Generator:
    for y in range(origin[1], origin[1] + shape[1]):
        for x in range(origin[0], origin[0] + shape[0]):
            yield (x, y)

def circle_seq(center: tuple[int, int], radius: int) -> Generator:
    def ends(half_chord: float):
        x_left = round(center[0] - half_chord)
        x_right = round(center[0] + half_chord)
        return x_left, x_right

    center = round(center[0]), round(center[1])
    radius = radius
    r_sq = radius ** 2
    caps_r = 0
    for d in range(1, radius):
        half_chord = sqrt(r_sq - d**2)
        x_left, x_right = ends(half_chord)
        for y in (center[1] - d, center[1] + d):
            yield from line_seq((x_left, y), (x_right, y))
        
        if x_right - x_left == 2 * radius:
            caps_r += 1

    x_left, x_right = ends(caps_r)
    for y in (center[1] - radius, center[1] + radius):
        yield from line_seq((x_left, y), (x_right, y))

    x_left, x_right = ends(radius)
    y = center[1]
    yield from line_seq((x_left, y), (x_right, y))

def polygon_seq(n: int, center: tuple[int, int], radius: int, offset: float = 0.0) -> Generator:
    if n < 1:
        return None
    elif n == 1:
        yield center
    else:
        da = 2 * pi / n
        vert_x = lambda angle: int(sin(angle) * radius) + center[0]
        vert_y = lambda angle: int(cos(angle) * radius) + center[1]
        prev = vert_x(offset), vert_y(offset)
        first = prev
        for vert in range(1, n):
            angle = offset + vert * da
            pos = vert_x(angle), vert_y(angle)
            yield from line_seq(prev, pos, 0)
            prev = pos
        yield from line_seq(pos, first)
