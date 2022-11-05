from dataclasses import dataclass, field
from functools import cached_property
from json import load
from os import system
from pathlib import Path
from sys import argv, path
from typing import Iterator

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
        """render text wrapping lines on the right edge starting at pos

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

    def letter_rect(self, pos: tuple[int, int]) -> Rect:
        return Rect(pos[0] * self.dot_size[0], pos[1] * self.line_size[1], self.dot_size[0], self.line_size[1])

    def put_letter(self, letter: str, pos: tuple[int, int], clear: bool = True) -> None:
        assert len(letter) == 1
        assert 0 <= pos[0] <= self.shape[0]
        assert 0 <= pos[1] <= self.shape[1]

        letter_render = self.font.render(letter, self.antialias, self.color)
        rect = self.letter_rect(self, pos)
        if clear:
            self.render.fill(self.backcolor, rect)
        self.render.blit(letter_render, rect)

    def img(self) -> Surface:
        return scale(self.render, self.full_res)       

if __name__ == '__main__':
    """returns error code
    0 - Success
    1 - Couldn't load 'settings.json' file
    """
    project_dir: Path = Path(argv[1]) 
    print(project_dir.as_posix())

    settings = project_dir / 'settings.json'
    out_dir = project_dir / 'out'

    path.append(project_dir.as_posix())
    from callback import _callback
    
    _SETTINGS: dict = {}
    with open(settings, 'r') as file:
        _SETTINGS = load(file)
    if not _SETTINGS:
        raise FileNotFoundError('Not found settings.json')

    _TEXT_RENDER_KEYS = set(
        ['shape', 'full_res', 'color', 'backcolor', 'antialias']
        )
    _TEXT_RENDER_SETTINGS = dict(
        [(k, v) for k, v in _SETTINGS.items() if k in _TEXT_RENDER_KEYS]
        )

    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode(_SETTINGS['screen_size'])
    clock = Clock()
    font = Font(project_dir / _SETTINGS['font_name'], _SETTINGS['font_size'])

    _TEXT_RENDER_SETTINGS['font'] = font    
    design = TextRender(**_TEXT_RENDER_SETTINGS)

    action: Iterator[bool] = _callback(design)

    running = True
    frame = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

        if not next(action, False):
            running = False
            break

        render = design.img()
        
        screen.fill(_SETTINGS['backcolor'])
        screen.blit(
            render,
            render.get_rect(center = screen.get_rect().center))

        pygame.display.update()

        if _SETTINGS['record'] and _SETTINGS['record'][0] <= frame < _SETTINGS['record'][1]:
            save(screen, out_dir / f'frame_{frame:0>5}.png')

        if frame >= _SETTINGS['quit']:
            running = False
            
        frame += 1
        clock.tick(_SETTINGS['FPS'])

    if _SETTINGS['record']:
        fps = _SETTINGS['FPS']
        system(f'ffmpeg -r {fps} -i ' + (out_dir / f'frame_%05d.png').as_posix() + ' -vcodec mpeg4 -y -r 30  ' + (out_dir / 'movie.mp4').as_posix())
    
    pygame.quit()

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
