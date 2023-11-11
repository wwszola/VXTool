from VXTool.callback import CallbackProcess
from VXTool.core import Color, Dot, Buffer
from VXTool.util import grid_seq

from .settings import colors, CONFIG

class Callback(CallbackProcess):
    def setup(self):
        self.base_dot: Dot = Dot(
            pos = (-1, -1), 
            letter = '█', 
            color = Color(0, 0, 0), 
            font_name="primary",
            clear = True
        )

        self.screen = Buffer()
        self.grid = list(grid_seq(CONFIG["shape"]))

    def update(self):
        self.clear()

        self.screen.clear()

        for pos in self.grid:
            dot = self.base_dot.variant(pos = pos, clear = False)
            self.screen.put(dot.variant(letter = 'A'))
            self.screen.put(dot.variant(letter = 'B', color = colors['RED']))
            self.screen.put(dot.variant(letter = 'C', color = colors['GREEN']))
            self.screen.put(dot.variant(letter = 'D', color = colors['BLUE']))

        self.draw(self.screen)
        self.present()