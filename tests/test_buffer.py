import unittest

from util import Timer

from VXTool.core import Color, Dot, Buffer

class BufferTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.some_dots = [
            Dot(pos=(0, 0), letter='A', clear=False),
            Dot(pos=(0, 0), letter='B', clear=True),
            Dot(pos=(0, 0), letter='C', clear=False),
            Dot(pos=(0, 1), letter='D', clear=False, backcolor=None),
            Dot(pos=(0, 1), letter='E', clear=False, backcolor=Color(255, 255, 255)),
            Dot(pos=(0, 1), letter='F', clear=False, backcolor=None),
            Dot(pos=(0, 2), letter='G', clear=False),
            Dot(pos=(0, 2), letter='H', clear=False),
            Dot(pos=(0, 2), letter='I', clear=False),
            Dot(pos=(0, 3), letter='J', clear=False),
            Dot(pos=(0, 3), letter='K', clear=False),
            Dot(pos=(0, 3), letter='L', clear=True)
        ]

    def setUp(self) -> None:
        self.buffer = Buffer()

    def test_put(self):
        dots = BufferTestCase.some_dots[:6]
        for dot in dots:
            self.buffer.put(dot)
        self.assertDictEqual(
            self.buffer._container,
            {(0, 0): dots[1:3], (0, 1): dots[4:6]}
        )

    def test_put_timer(self):
        dots = BufferTestCase.some_dots
        length = len(dots)
        t = Timer(
            number=1000000, 
            func = lambda i: self.buffer.put(dots[i%length])
        ).run()
        print(self.id(), t.stats)
