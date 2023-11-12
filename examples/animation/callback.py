from VXTool.callback import CallbackProcess
from VXTool.core import AnimatedBuffer, AnimatedDot, Color, Dot

# from VXTool.util import


class Callback(CallbackProcess):
    def setup(self):
        self.base_dot: Dot = Dot(
            pos=(-1, -1),
            letter="█",
            color=Color(0, 0, 0),
            font_name="primary",
            clear=True,
        )

        self.pulse = self.base_dot.variant(AnimatedDot, pos=(5, 5))
        self.pulse.op_set(0, "letter", "ABCD")
        self.pulse.op_move(1, (1, 0), 3)
        self.pulse.op_move(4, (-3, 0))
        self.pulse.op_jmp(4, 0)

        self.screen = AnimatedBuffer()
        self.screen.put(self.pulse)

    def update(self):
        self.clear()

        self.screen.advance()
        self.draw(self.screen)

        self.present()
