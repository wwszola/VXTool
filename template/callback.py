from typing import Iterator

from text_render import TextRender, Buffer, Dot
from text_render import Font
from text_render import line_seq

def _callback(design: TextRender, user_settings: dict) -> Iterator[bool]:
    """entry point
    mark end of the each frame with yield True
    return None or yield False to quit
    """
    UniVGA16: Font = user_settings['fonts']['UniVGA16'][16]
    base_dot: Dot = Dot(
        pos = (-1, -1), 
        letter = '█', color = (100, 70, 140), 
        font = UniVGA16, clear = True)
    
    # two lines below are required before drawing anything on design
    design.block_size = base_dot.size 
    design.resize_screen()

    # setup your sketch
    y = design.shape[1]//2
    line = list(line_seq((0, y), (design.shape[0], y)))
    text = 'Hello world'

    layer1 = Buffer()

    # generating a dot for every letter in text
    dots = (base_dot.variant(letter = letter, pos = pos) for letter, pos in zip(text, line))
    layer1.extend(dots)

    # this line does only drawing in here
    design.draw(layer1)

    while True:
        yield True

    return None