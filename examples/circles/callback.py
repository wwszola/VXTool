from VXTool.callback import CallbackProcess
from VXTool.core import Buffer, Color, Dot
from VXTool.util import midpoint_circle, scanline_circle

from .settings import CONFIG

SHAPE = CONFIG["shape"]
CENTER1 = 1 * SHAPE[0] // 4, SHAPE[1] // 2
CENTER2 = 3 * SHAPE[0] // 4, SHAPE[1] // 2


class Callback(CallbackProcess):
    def setup(self):
        self.base_dot: Dot = Dot(
            pos=(-1, -1),
            letter="█",
            color=Color(0, 0, 0),
            font_name="primary",
            clear=True,
        )

        self.circle_radius = 10
        self.layer1 = Buffer()
        self.layer2 = Buffer()

        self.draw_circle()

    def on_KEYDOWN_UP(self, attrs):
        self.circle_radius = min(self.circle_radius + 1, SHAPE[1] // 2)
        self.draw_circle()

    def on_KEYDOWN_DOWN(self, attrs):
        self.circle_radius = max(self.circle_radius - 1, 0)
        self.draw_circle()

    def draw_circle(self):
        self.layer1.clear()
        for pos in midpoint_circle(CENTER1, self.circle_radius):
            self.layer1.put(self.base_dot.variant(pos=pos))
        self.layer2.clear()
        for pos in scanline_circle(CENTER2, self.circle_radius):
            self.layer2.put(self.base_dot.variant(pos=pos))

    def update(self):
        self.clear()
        self.draw(self.layer1)
        self.draw(self.layer2)
        self.present()
