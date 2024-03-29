from VXTool.callback import CallbackProcess
from VXTool.core import Buffer, Color, Dot
from VXTool.util.picture import rect_fill

from .settings import CONFIG, colors


class Callback(CallbackProcess):
    def setup(self):
        self.base_dot: Dot = Dot(
            pos=(-1, -1),
            letter="█",
            color=Color(0, 0, 0),
            font_name="primary",
            clear=True,
        )

        self.screen = Buffer()
        self.grid = list(rect_fill(CONFIG["shape"]))

    def update(self):
        self.clear()

        self.screen.clear()

        for pos in self.grid:
            dot = self.base_dot.variant(pos=pos, clear=False)
            self.screen.put(dot.variant(letter="A"))
            self.screen.put(dot.variant(letter="B", color=colors["RED"]))
            self.screen.put(dot.variant(letter="C", color=colors["GREEN"]))
            self.screen.put(dot.variant(letter="D", color=colors["BLUE"]))

        self.draw(self.screen)
        self.present()
