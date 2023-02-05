from typing import Generator

from itertools import cycle
from math import sin

from text_render import TextRender, Buffer, Dot
from text_render import Font, Color
from text_render import words_line

def _callback(design: TextRender, user_settings: dict) -> Generator:
    """entry point
    first mark end of your setup with yield True
    then mark end of the each frame with yield True
    yield False to quit
    """
    UniVGA16: Font = user_settings['fonts']['UniVGA16'][16]
    base_dot: Dot = Dot(
        pos = (-1, -1), 
        letter = '█', 
        color = Color(100, 70, 140), 
        font = UniVGA16, clear = False)
    
    # two lines below are required before drawing anything on design
    design.block_size = base_dot.size 
    design.resize_screen()

    colors = user_settings["COLORS"]

    layer1 = Buffer()
    texts = [
        "This is a",
        "test for ",
        "colors.  ",
    ]
    color = colors["RED"]
    for i, line in enumerate(texts):
        layer1.extend((
            base_dot.variant(pos = pos, letter = letter, color = color)
            for pos, letter in words_line(line, (1, i + 1))
    ))

    layer2 = Buffer()
    texts2 = [
        "            ",
        "Is this     ",
        "transparent?",
    ]

    color = colors["BLUE"]
    color = Color(color.r, color.g, color.b, 192)
    for i, line in enumerate(texts2):
        layer2.extend((
            base_dot.variant(pos = pos, letter = letter, color = color)
            for pos, letter in words_line(line, (1, i + 1))
    ))

    events = yield True

    # your draw loop
    while True:
        design.clear()

        design.draw(layer1)
        design.draw(layer2)

        events = yield True

    yield False