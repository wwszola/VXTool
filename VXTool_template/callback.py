from VXTool.callback import CallbackProcess
from VXTool.core import Color, Dot, Buffer
from VXTool.util import words_line

from .settings import colors

class Callback(CallbackProcess):
    def setup(self):
        self.base_dot: Dot = Dot(
            pos = (-1, -1), 
            letter = '█', 
            color = Color(0, 0, 0), 
            font_name = "primary",
            clear = True
        )

    def update(self):
        buffer = Buffer()
        for pos, letter in words_line("Hello", (0, 0)):
            buffer.put(self.base_dot.variant(pos = pos, letter = letter))
        self.send(buffer)
