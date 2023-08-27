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
        # lines above are needed at the beginning to initialize
        # for more see example block_size

        # access the colors that were provided in settings.json file
        colors = self.user_settings["COLORS"]

        # this picture will be composed of three separate layers
        # each one represented by Buffer object

        # layer1 has multiple lines of text, in color RED
        layer1 = Buffer()
        text1 = [
            "This is a",
            "test for ",
            "colors.  ",
        ]
        color = colors["RED"]
        for i, line in enumerate(text1): # for every line of the text
            layer1.extend(( # put multiple dots
                self.base_dot.variant(pos = pos, letter = letter, color = color)
                # arranged by generator returned by util.words_line(text, pos)
                for pos, letter in words_line(line, (1, i + 1))
        ))

        # layer2 has text too, but in color BLUE with transparency
        layer2 = Buffer()
        text2 = [
            "            ",
            "Is this     ",
            "transparent?",
        ]
        color = colors["BLUE"]
        color = Color(color.r, color.g, color.b, 127)
        for i, line in enumerate(text2):
            layer2.extend((
                self.base_dot.variant(pos = pos, letter = letter, color = color)
                for pos, letter in words_line(line, (1, i + 1))
        ))

        # layer3 has a diagonal line drawn with full block green dots
        layer3 = Buffer()
        P1, P2 = (3, 2), (13, 6)
        layer3.extend((
            self.base_dot.variant(pos = pos, color = colors["GREEN"])
            for pos in line_seq(P1, P2)
        ))

        # this picture is static, merge the layers together
        self.screen = Buffer()
        self.screen.merge(layer3)
        self.screen.merge(layer1)
        self.screen.merge(layer2)

    def update(self):
        self.send('Screen', self.screen)

    def on_KEYDOWN(self, attrs: dict):
        # every time a key is pressed down, draw full name of it
        # dot with attr clear set to True, overwrites anything on its pos
        dot = self.base_dot.variant(clear = True)
        self.screen.extend(
            dot.variant(pos = pos, letter = letter)
            for pos, letter in words_line(attrs['key_name'], (1, 4))
        )
