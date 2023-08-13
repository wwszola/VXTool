from VXTool.callback import CallbackProcess
from VXTool.render import RENDER_MSG
from VXTool.core import Color, Dot, Buffer
from VXTool.util import words_line, line_seq

class Callback(CallbackProcess):
    def setup(self):
        self.base_dot: Dot = Dot(
            pos = (-1, -1), 
            letter = '█', 
            color = Color(100, 70, 140), 
            font_family = "UniVGA16",  
            font_size = 16,
            clear = False
        )
        self.send('Screen', None, RENDER_MSG.PROCEDURE | RENDER_MSG.SET_BLOCK_SIZE, self.base_dot)

        colors = self.user_settings["COLORS"]

        layer1 = Buffer()
        texts = [
            "This is a",
            "test for ",
            "colors.  ",
        ]
        color = colors["RED"]
        for i, line in enumerate(texts):
            layer1.extend((
                self.base_dot.variant(pos = pos, letter = letter, color = color)
                for pos, letter in words_line(line, (1, i + 1))
        ))

        layer2 = Buffer()
        texts2 = [
            "            ",
            "Is this     ",
            "transparent?",
        ]

        color = colors["BLUE"]
        color = Color(color.r, color.g, color.b, 192)
        for i, line in enumerate(texts2):
            layer2.extend((
                self.base_dot.variant(pos = pos, letter = letter, color = color)
                for pos, letter in words_line(line, (1, i + 1))
        ))

        layer3 = Buffer()
        P1, P2 = (3, 2), (13, 6)
        layer3.extend((
            self.base_dot.variant(pos = pos, color = colors["GREEN"])
            for pos in line_seq(P1, P2)
        ))

        self.screen = Buffer()
        self.screen.merge(layer3)
        self.screen.merge(layer1)
        self.screen.merge(layer2)

        self.text = 'ABCDEFGHIJK'

    def update(self):
        if self.updates_count > 0:
            self.screen.erase_at((3, 3))
        self.screen.put(self.base_dot.variant(
            pos = (3, 3), 
            letter = self.text[self.updates_count%len(self.text)],
            clear = False
        ))
        letter = self.text[self.updates_count % len(self.text)]
        self.send('Screen', self.screen)

    def on_KEYDOWN_SPACE(self, attrs: dict):
        self.on_KEYDOWN(attrs)
        self.text = 'AUTOMATIC'

    def on_KEYDOWN(self, attrs: dict):
        dot = self.base_dot.variant(clear=True)
        self.screen.extend(
            dot.variant(pos = pos, letter = letter)
            for pos, letter in words_line(attrs['key_name'], (1, 4))
        )