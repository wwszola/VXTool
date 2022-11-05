from typing import Iterator

from text_render import TextRender

def _callback(design: TextRender, user_settings: dict) -> Iterator[bool]:
    """entry point
    make changes to design
    mark end of the each frame with yield True
    return None or yield False to quit
    """
    design.put_words('Hello, world!', (0, 0))
    while True:
        yield True

    return None