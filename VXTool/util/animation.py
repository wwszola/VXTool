import random

from ..core import AnimatedDot, Color


def random_walk_x(dot: AnimatedDot, delta_time: int = 0, length: int = 1):
    for i in range(length):
        x = random.choice([-1, -1, 0, 1, 1])
        dot.op_move(delta_time + i, (x, 0))
    return dot


def fade_in_fade_out(
    dot: AnimatedDot, delta_time: int = 0, length: int = 1, colors: list[Color] = []
):
    dot.op_set(delta_time, "color", colors)
    dot.op_set(delta_time + length - len(colors), "color", colors[::-1])
    return dot


def spell_and_stop(dot: AnimatedDot, delta_time: int = 0, text: str = ""):
    dot.op_set(delta_time, "letter", text)
    dot.op_stop(delta_time + len(text))
    return dot


def loop_letters(
    dot: AnimatedDot, delta_time: int = 0, text: str = "", offset: int = 0
):
    offset = offset % len(text)
    dot.op_set(delta_time, "letter", text[offset:])
    dot.op_set(delta_time + offset, "letter", text[:offset])
    dot.op_jmp(len(text), 0)
    return dot
