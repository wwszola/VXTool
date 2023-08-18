from VXTool.callback import CallbackProcess
from VXTool.render import RENDER_MSG
from VXTool.core import Color, Dot, Buffer
# from VXTool.util import 

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

        colors = self.user_settings["COLORS"]
        
    def update(self):
        self.send('Screen', None, RENDER_MSG.NO_CHANGE)
