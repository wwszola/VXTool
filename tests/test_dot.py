import unittest

from util import Timer

from VXTool.core import Dot, Color


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

    def test_dot_hash(self):
        dot = DotTestCase.base_dot
        new_dot = dot.variant(
            pos = (1, 1)
        )
        self.assertEqual(hash(dot), hash(new_dot), 'pos changed hash')
        new_dot = dot.variant(
            letter = 'B',
            color = Color(0, 255, 0),
            backcolor = Color(255, 0, 255),
            font_family = 'FONT2',
            font_size = 16,
            clear = False
        )
        self.assertNotEqual(hash(dot), hash(new_dot), 'attr different from pos didn\' changed hash')

    def test_variant(self):
        new_dot = DotTestCase.base_dot.variant(
            pos = (1, 1), letter = 'B', clear = False
        )
        self.assertEqual(new_dot.pos, (1, 1))
        self.assertEqual(new_dot.letter, 'B')
        self.assertEqual(new_dot.clear, False)

    def test_variant_performance(self):
        dot = DotTestCase.base_dot
        p = Timer(
            number = 100000, 
            func = lambda _: dot.variant(
                pos = (2, 2), 
                letter = 'A', 
                color = Color(125, 125, 255),
                font_size = 16
            )
        ).run()
        print(self.id(), p.stats)

    def test_hash_performance(self):
        dot = DotTestCase.base_dot
        p = Timer(
            number = 100000,
            func = lambda _: hash(dot)
        ).run()
        print(self.id(), p.stats)
