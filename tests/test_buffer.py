import unittest

from collections import defaultdict

from .util import Timer

from VXTool.core import Color, Dot, Buffer


class MockBuffer():
    def __init__(self, _container: dict = dict()):
        self._container = defaultdict(list)
        if _container:
            for key, value in _container.items():
                self._container[key] = value[:]

    def put(self, dot: Dot):
        local = self._container[dot.pos]
        if dot.clear or dot.backcolor is not None:
            local.clear()
        local.append(dot)

    def diff(self, other):
        diff = MockBuffer()
        clear_mask = set(self._container.keys()) - (other._container.keys())
        for pos in other._container.keys():
            if pos not in self._container:
                clear_mask.add(pos)
                diff._container[pos] = other._container[pos][:]
            else:
                self_local = self._container[pos]
                other_local = other._container[pos]
                i = 0
                for (dot1, dot2) in zip(self_local, other_local):
                    if dot1 != dot2:
                        break
                    i += 1
                if i == len(self_local):
                    if i != len(other_local):
                        diff._container[pos] = other_local[i:]
                else:
                    clear_mask.add(pos)
                    diff._container[pos] = other_local[:]

        return diff, clear_mask
    
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

    def test_put_alternative(self):
        buffer = MockBuffer()
        buffer._container.clear() # Why this is needed ????
        dots = BufferTestCase.some_dots[:6]
        for dot in dots:
            buffer.put(dot)
        self.assertDictEqual(
            buffer._container,
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

    def test_diff(self):
        dots = BufferTestCase.some_dots
        buffer1 = Buffer({
            (0, 0): [dots[0]],
            (0, 1): [dots[4]],
            (0, 2): [dots[6], dots[7]]
        })
        buffer2 = Buffer({
            (0, 0): [dots[1]],
            (0, 1): [dots[4], dots[5]]
        })
        diff, clear_mask = buffer1.diff(buffer2)
        self.assertDictEqual(
            diff._container, 
            {(0, 0): [dots[1]], (0, 1): [dots[5]]}
        )
        self.assertSetEqual(
            clear_mask, 
            set([(0, 0), (0, 2)])
        )

    def test_diff_timer(self):
        dots = BufferTestCase.some_dots
        buffer1 = Buffer({
            (0, 0): [dots[0]],
            (0, 1): [dots[4]],
            (0, 2): [dots[6], dots[7]],
            (0, 3): [dots[9], dots[10]]
        })
        buffer2 = Buffer({
            (0, 0): [dots[1], dots[2]],
            (0, 1): [dots[4], dots[5], dots[5]],
            (0, 3): [dots[11]]
        })
        t = Timer(
            number = 10000, 
            func = lambda _: buffer1.diff(buffer2)
        ).run()
        print(self.id(), t.stats)

    def test_diff_alternative(self):
        dots = BufferTestCase.some_dots
        buffer1 = MockBuffer({
            (0, 0): [dots[0]],
            (0, 1): [dots[4]],
            (0, 2): [dots[6], dots[7]]
        })
        buffer2 = MockBuffer({
            (0, 0): [dots[1]],
            (0, 1): [dots[4], dots[5]]
        })
        diff, clear_mask = buffer1.diff(buffer2)
        self.assertDictEqual(
            diff._container, 
            {(0, 0): [dots[1]], (0, 1): [dots[5]]}
        )
        self.assertSetEqual(
            clear_mask, 
            set([(0, 0), (0, 2)])
        )

    def test_diff_alternative_timer(self):
        dots = BufferTestCase.some_dots
        buffer1 = MockBuffer({
            (0, 0): [dots[0]],
            (0, 1): [dots[4]],
            (0, 2): [dots[6], dots[7]],
            (0, 3): [dots[9], dots[10]]
        })
        buffer2 = MockBuffer({
            (0, 0): [dots[1], dots[2]],
            (0, 1): [dots[4], dots[5], dots[5]],
            (0, 3): [dots[11]]
        })
        t = Timer(
            number = 10000, 
            func = lambda _: buffer1.diff(buffer2)
        ).run()
        print(self.id(), t.stats)