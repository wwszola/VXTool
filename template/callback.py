from typing import Iterator

from text_render import TextRender

def _callback(design: TextRender) -> Iterator[bool]:
    """entry point
    make changes to design
    mark end of the each frame with yield True
    return None or yield False to quit
    """
    for _ in range(8):
        yield True
    
    return None