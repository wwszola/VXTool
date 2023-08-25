from VXTool.callback import CallbackProcess
from VXTool.render import RENDER_MSG
from VXTool.core import Color, Dot, Buffer
from VXTool.util import words_line, grid_seq

class Callback(CallbackProcess):
    def setup(self):
        # it's helpful to make a "base" dot for every font you use
        self.base_dot: Dot = Dot(
            pos = (-1, -1), 
            letter = '█', 
            color = Color(0, 0, 0), 
            font_family = "UniVGA16",  
            font_size = 16,
            clear = True
        )

        # At least once, before drawing anything you must send entry
        # with RENDER_MSG.PROCEDURE | RENDER_MSG.SET_BLOCK_SIZE flag,
        # to prepare drawing surfaces.
        # Argument to this entry may be either tuple[int, int] or Dot
        # The basic solution is to pass a Dot
        self.send('Screen', None, RENDER_MSG.PROCEDURE | RENDER_MSG.SET_BLOCK_SIZE, self.base_dot)

        self.shape = self.widgets_info['Screen']['shape']
        self.screen = Buffer()

    def update(self):
        self.screen.clear()
        for x, y in grid_seq(self.shape):
            self.screen.put(self.base_dot.variant(pos = (x, y), letter = 'X'))
        self.send('Screen', self.screen)

    def on_KEYDOWN_A(self, attrs: dict):
        # Solution A
        # Use a Dot as an argument. Then block_size will be equal to the dot's size.
        self.send('Screen', None, RENDER_MSG.PROCEDURE | RENDER_MSG.SET_BLOCK_SIZE, self.base_dot)

    def on_KEYDOWN_B(self, attrs: dict):
        # read a size of a specific font
        dot_size = self.fonts_info['UniVGA16', 16]['size']
        # modify the line below to get different results
        block_size = dot_size[0] * 2, dot_size[1] * 2
        # Solution B
        # Use a tuple[int, int]. Then block_size is the value.
        self.send('Screen', None, RENDER_MSG.PROCEDURE | RENDER_MSG.SET_BLOCK_SIZE, block_size)


