from VXTool.callback import CallbackProcess
from VXTool.render import RENDER_MSG
from VXTool.core import Color, Dot, Buffer
from VXTool.util import grid_seq

class Callback(CallbackProcess):
    def setup(self):
        self.base_dot: Dot = Dot(
            pos = (-1, -1), 
            letter = '█', 
            color = Color(0, 0, 0), 
            font_family = "UniVGA16",  
            font_size = 16,
            clear = True
        )
        self.send('Screen', None, RENDER_MSG.PROCEDURE | RENDER_MSG.SET_BLOCK_SIZE, self.base_dot)

        self.colors = self.user_settings["COLORS"]
        
        self.screen = Buffer()
        self.grid = list(grid_seq(self.widgets_info['Screen']['shape']))

    def update(self):
        self.screen.clear()

        for pos in self.grid:
            dot = self.base_dot.variant(pos = pos, clear = False)
            self.screen.put(dot.variant(letter = 'A'))
            self.screen.put(dot.variant(letter = 'B', color = self.colors['RED']))
            self.screen.put(dot.variant(letter = 'C', color = self.colors['GREEN']))
            self.screen.put(dot.variant(letter = 'D', color = self.colors['BLUE']))

        self.send('Screen', self.screen)
