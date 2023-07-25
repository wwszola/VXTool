import unittest

from .util import Timer

from VXTool.core import Color, Dot, Buffer


class MockBuffer():
    def __init__(self):
        self._container = dict()

    def put(self, dot: Dot):
        local: list[Dot] = self._container.setdefault(dot.pos, [])
        if dot.clear or dot.backcolor is not None:
            local.clear()
        local.append(dot)

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
        ]

    def setUp(self) -> None:
        self.buffer = Buffer()

    def test_put(self):
        dots = BufferTestCase.some_dots
        for dot in dots:
            self.buffer.put(dot)
        container = self.buffer._container
        self.assertDictEqual(
            container,
            {(0, 0): dots[1:3], (0, 1): dots[4:6]}
        )

    def test_put_alternative(self):
        self.buffer = MockBuffer()
        dots = BufferTestCase.some_dots
        for dot in dots:
            self.buffer.put(dot)
        container = self.buffer._container
        self.assertDictEqual(
            container,
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

    def test_put_alternative_timer(self):
        self.buffer = MockBuffer()
        dots = BufferTestCase.some_dots
        length = len(dots)
        t = Timer(
            number=1000000, 
            func = lambda i: self.buffer.put(dots[i%length])
        ).run()
        print(self.id(), t.stats)