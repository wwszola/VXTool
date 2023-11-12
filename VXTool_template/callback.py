from VXTool.callback import CallbackProcess
from VXTool.core import Color, Dot, Buffer

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

    def update(self):
        self.clear()
        self.present()
