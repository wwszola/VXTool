from VXTool.callback import CallbackProcess
from VXTool.render import RENDER_MSG
from VXTool.core import Color, Dot, Buffer, AnimatedDot, AnimatedBuffer
# from VXTool.util import 

class Callback(CallbackProcess):
    def setup(self):
        font_sizes = [16 + i*2 for i in range(5)]
        self.base_dot: Dot = Dot(
            pos = (-1, -1), 
            letter = '█', 
            color = Color(0, 0, 0), 
            font_family = "UniVGA16",  
            font_size = font_sizes[-1],
            clear = True
        )
        self.send('Screen', None, RENDER_MSG.PROCEDURE | RENDER_MSG.SET_BLOCK_SIZE, self.base_dot)

        colors = self.user_settings["COLORS"]

        self.pulse = AnimatedDot(**self.base_dot.__dict__)
        self.pulse.pos = (5, 5)
        self.pulse.op_set(0, 'letter', 'ABCD')
        self.pulse.op_move(1, (1, 0), 3)
        self.pulse.op_move(4, (-3, 0))
        self.pulse.op_jmp(4, 0)

        self.screen = AnimatedBuffer()
        self.screen.put(self.pulse)

        
    def update(self):
        self.screen.advance()
        self.send('Screen', self.screen)
