from pathlib import Path

import pygame.font as pgfont

def construct_font_name(path: str | Path, ptsize: int, name: str = "") -> str:
    if isinstance(path, str):
        path = Path(path)
    filename = path.name.split('.')[0]
    return f"{filename}{ptsize}"

class FontInfo:
    def __init__(self, path: str | Path, ptsize: int, name: str = ""):
        if isinstance(path, str):
            path = Path(path)
        self.path: Path = path
        self.ptsize: int = ptsize
        if len(name) == 0:
            name = construct_font_name(self.path, self.ptsize)
        self.name: str = name

class FontBank:
    def __init__(self):
        self._fonts: dict[pgfont.Font] = dict()
        if not pgfont.get_init():
            pgfont.init()

    def load(self, font_info: FontInfo):
        font = pgfont.Font(font_info.path, font_info.ptsize)
        self._fonts[font_info.name] = font

    def load_all(self, fonts_info: list[FontInfo]):
        for font_info in fonts_info:
            self.load(font_info)

    def get(self, name: str) -> pgfont.Font:
        return self._fonts[name]
