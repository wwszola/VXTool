import unittest
import time

from VXTool.core import Dot, Color

class Profiler:
    def __init__(self, number, func):
        self.number = number
        self.func = func
        self.start_time = 0.0
        self.delta = 0.0
        self.average = 0.0

    def run(self):
        self.start_time = time.time()
        for i in range(self.number):
            (self.func)()
        self.delta = time.time() - self.start_time
        self.average = self.delta/self.number

        return self
    
class DotTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dot = Dot(
            pos = (0, 0),
            letter = 'A',
            color = Color(0, 0, 0),
            backcolor = Color(255, 255, 255),
            font_family = 'FONT',
            font_size = 8,
            clear = True
        )

    def test_variant(self):
        new_dot = DotTestCase.base_dot.variant(
            pos = (1, 1), letter = 'B', clear = False
        )
        self.assertEqual(new_dot.pos, (1, 1))
        self.assertEqual(new_dot.letter, 'B')
        self.assertEqual(new_dot.clear, False)

    def test_variant_performance(self):
        dot = DotTestCase.base_dot
        p = Profiler(
            number = 100000, 
            func = lambda: dot.variant(
                pos = (2, 2), 
                letter = 'A', 
                color = Color(125, 125, 255),
                font_size = 16
            )
        ).run()
        print("{} delta: {:.2}s average: {:.2}s".format(self.id(), p.delta, p.average))

    def test_hash_performance(self):
        dot = DotTestCase.base_dot
        p = Profiler(
            number = 100000,
            func = lambda: hash(dot)
        ).run()
        print("{} delta: {:.2}s average: {:.2}s".format(self.id(), p.delta, p.average))
