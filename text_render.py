from dataclasses import dataclass, field
from functools import cached_property
from json import load
from pathlib import Path
from sys import argv, path
from typing import Iterator, Iterable

import pygame
from pygame import Surface, Rect
from pygame.font import Font
from pygame.transform import scale
from pygame.time import Clock
from pygame.image import save

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

@dataclass
class TextRender:
    shape: tuple[int, int]
    full_res: tuple[int, int]

    font: Font
    color: tuple[int, int, int] = WHITE
    backcolor: tuple[int, int, int] = BLACK
    antialias: bool = True
    
    render: Surface = field(init = False)
    buffer: list = field(default_factory = list)
    buffer_letter: str = field(default = ' ')

    def __post_init__(self):
        print('Text Render __post_init__')
        print(self.dot_size, self.line_size, self.full_size)
        self.render: Surface = Surface(self.full_size, depth = 24)
        self.render.fill(self.backcolor)

    @cached_property
    def dot_size(self) -> tuple[int, int]:
        return self.font.size('█')

    @cached_property
    def line_size(self) -> tuple[int, int]:
        return (self.shape[0] * self.dot_size[0], self.dot_size[1])

    def line_rect(self, idx: int) -> Rect:
        return Rect(0, idx * self.line_size[1], self.line_size[0], self.line_size[1])

    @cached_property
    def full_size(self) -> tuple[int, int]:
        return (self.shape[0] * self.dot_size[0], self.shape[1] * self.dot_size[1])

    def put_line(self, text: str, line_idx: int, clear: bool = True):
        assert(len(text) == self.shape[0])
        assert(0 <= line_idx < self.shape[1])
        line_render = self.font.render(text, self.antialias, self.color)
        rect = self.line_rect(line_idx)
        if clear:
            self.render.fill(self.backcolor, rect)
        self.render.blit(line_render, rect)

    def word_rect(self, length: int, pos: tuple[int, int]) -> Rect:
        return Rect(pos[0] * self.dot_size[0], pos[1] * self.line_size[1], length * self.dot_size[0], self.line_size[1])
    
    def put_words(self, text: str, pos: tuple[int, int], clear: bool = True) -> str:
        """render text wrapping lines starting at pos

        renders text only up to right-bottom corner

        Parameters:
        text: str
        pos: tuple[int, int]
            row_idx, line_idx
        clear: bool = True
            if True, fill with self.backcolor before blitting to self.render

        Returns:
        str
            if text doesn't end at right-bottom corner, return what's left
        """
        assert 0 <= pos[0] <= self.shape[0]
        assert 0 <= pos[1] <= self.shape[1] 
        
        while len(text) > 0 and pos[1] < self.shape[1]:
            cut = self.shape[0] - pos[0]
            word = text[:cut]
            text = text[cut:]

            word_render = self.font.render(word, self.antialias, self.color)
            rect = self.word_rect(len(word), pos)
            if clear:
                self.render.fill(self.backcolor, rect)
            self.render.blit(word_render, rect)
            
            if pos[0] + len(word) >= self.shape[0]:
                pos = (0, pos[1] + 1)
            else:
                pos = (pos[0] + len(word), pos[1])
        return text

    @cached_property
    def grid_rect(self) -> Rect:
        return Rect((0, 0), self.shape)

    def put_words_bound(self, text: str, region: Rect, clear: bool = True) -> str:
        assert region.clip(self.grid_rect).size
        pos = (0, 0)
        while len(text) > 0 and pos[1] < region.height:
            cut = region.width - pos[0]
            word = text[:cut]
            text = text[cut:]

            word_render = self.font.render(word, self.antialias, self.color)
            rect = self.word_rect(len(word), (pos[0] + region.left, pos[1] + region.top))
            if clear:
                self.render.fill(self.backcolor, rect)
            self.render.blit(word_render, rect)
            
            if pos[0] + len(word) >= region.width:
                pos = (0, pos[1] + 1)
            else:
                pos = (pos[0] + len(word), pos[1])
        return text


    def letter_rect(self, pos: tuple[int, int]) -> Rect:
        return Rect(pos[0] * self.dot_size[0], pos[1] * self.line_size[1], self.dot_size[0], self.line_size[1])

    def put_letter(self, letter: str, pos: tuple[int, int], clear: bool = True) -> None:
        assert len(letter) == 1
        assert 0 <= pos[0] <= self.shape[0]
        assert 0 <= pos[1] <= self.shape[1]

        letter_render = self.font.render(letter, self.antialias, self.color)
        rect = self.letter_rect(pos)
        if clear:
            self.render.fill(self.backcolor, rect)
        self.render.blit(letter_render, rect)

    def buffer_put(self, points: Iterable[tuple[int, int]]) -> None:
        self.buffer.extend(
            filter(lambda p: self.grid_rect.collidepoint(p), points)
            )            

    def buffer_blit(self, clear_buffer: bool = True, clear: bool = True) -> None:
        letter_render = self.font.render(self.buffer_letter, self.antialias, self.color, self.backcolor)
        blits = [(letter_render, self.letter_rect(p)) for p in self.buffer]
        if clear:
            for _, rect in blits: self.render.fill(self.backcolor, rect) 
        self.render.blits(blits)
        if clear_buffer:
            self.buffer.clear()
    
    def clear(self, region: Rect = None):
        if not region:
            region = self.grid_rect
        region = Rect(
            region.left * self.dot_size[0],
            region.top * self.dot_size[1],
            region.width * self.dot_size[0],
            region.height * self.dot_size[1]
            )
        self.render.fill(self.backcolor, region)

    def img(self) -> Surface:
        return scale(self.render, self.full_res)       

def _app(_SETTINGS: dict):
    pygame.init()
    screen = pygame.display.set_mode(_SETTINGS['render_size'])

    pygame.font.init()
    font = Font(
        _SETTINGS['project_dir'] / _SETTINGS['font_name'], 
        _SETTINGS['font_size']
        )
    _SETTINGS['TEXT_RENDER']['font'] = font   
    design = TextRender(**_SETTINGS['TEXT_RENDER'])
    clock = Clock()

    action: Iterator[bool] = _SETTINGS['_callback'](design, _SETTINGS['USER'])
    
    record = _SETTINGS.get('record', None)
    quit = _SETTINGS.get('quit', None)

    running = True
    frame = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    save(screen, _SETTINGS['out_dir'] / f'frame_{frame:0>5}.png')

        if not next(action, False):
            running = False
            break

        render = design.img()
        
        screen.fill(_SETTINGS['backcolor'])
        screen.blit(
            render,
            render.get_rect(center = screen.get_rect().center))

        pygame.display.update()

        if record and record[0] <= frame < record[1]:
            save(screen, _SETTINGS['out_dir'] / f'frame_{frame:0>5}.png')

        if quit and frame >= quit:
            running = False
            
        frame += 1
        clock.tick(_SETTINGS['FPS'])

    pygame.quit()

def _main():
    project_dir: Path = Path(argv[1]) 
    out_dir = project_dir / 'out'
    print(project_dir)

    _SETTINGS: dict = {
        "project_dir": project_dir,
        "out_dir": out_dir
    }
    settings = project_dir / 'settings.json'
    with open(settings, 'r') as file:
        _SETTINGS.update(load(file))

    _SETTINGS['TASKS']: dict = {
        'movie': _movie_task_call
    }
    
    if len(argv) > 2 and argv[2] in _SETTINGS['TASKS'].keys():
        call = _SETTINGS['TASKS'].get(argv[2], None)
        if call: call(argv[2:])
        return 2

    try:
        path.append(project_dir.as_posix())
        from callback import _callback
        assert _callback
        _SETTINGS['_callback'] = _callback
    except (ImportError, AssertionError) as e:
        print(e.msg)
        return 3
    
    _app(_SETTINGS)

    for task in _SETTINGS['end_tasks']:
        call = _SETTINGS['TASKS'][task]
        if call: call(_SETTINGS)

# Tasks
def _movie_task_str(settings: dict) -> str:
    """this is ffmpeg sequence that worked for me"""
    fps = settings['FPS']
    out_dir = settings['out_dir']
    return f'ffmpeg -framerate {fps} -i ' + (out_dir / f'frame_%05d.png').as_posix() + ' -c:v libx264 -pix_fmt yuv420p -vf scale=out_color_matrix=bt709 -r 30 ' + (out_dir / 'movie.mp4').as_posix()

def _movie_task_call(settings: dict, *args):
    from os import system
    system(_movie_task_str(settings))

if __name__ == '__main__':
    _main()

# Utility functions
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

def line_seq(p1: tuple[int, int], p2: tuple[int, int]) -> Iterator[tuple[int, int]]:
    """DDA line generating algorithm"""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    if abs(dx) >= abs(dy):
        step = abs(dx)
    else:
        step = abs(dy)
    dx, dy = dx / step, dy / step
    x, y = p1[0], p1[1]
    for _ in range(step + 1):
        yield round(x), round(y)
        x, y = x + dx, y + dy
