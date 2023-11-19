from math import cos, pi, sin, sqrt
from typing import Callable


def dda_line(p1: tuple[float, float], p2: tuple[float, float], end: int = 1):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    step = max(abs(dx), abs(dy))

    if step <= 1e-16:
        yield round(p1[0]), round(p1[1])
    else:
        dx, dy = dx / step, dy / step
        for i in range(round(step) + end):
            x = p1[0] + i * dx
            y = p1[1] + i * dy
            yield round(x), round(y)


def rect_fill(size: tuple[int, int]):
    for y in range(0, size[1]):
        for x in range(0, size[0]):
            yield (x, y)


def _circle_octant_symmetry(x: int, y: int):
    yield from ((x, y), (x, -y), (-x, y), (-x, -y), (y, x), (y, -x), (-y, x), (-y, -x))


def midpoint_circle(center: tuple[int, int], radius: int):
    p = (5 - 4 * radius) // 4
    x = 0
    y = radius
    while x <= y:
        yield from (
            (x + center[0], y + center[1]) for x, y in _circle_octant_symmetry(x, y)
        )
        x = x + 1
        p += 2 * x + 1
        if p >= 0:
            y = y - 1
            p -= 2 * y


def scanline_circle(center: tuple[int, int], radius: int):
    x = 0
    y = radius
    radius_sq = radius * radius
    while x <= y:
        y = round(sqrt(radius_sq - x * x))
        yield from (
            (x + center[0], y + center[1]) for x, y in _circle_octant_symmetry(x, y)
        )
        x = x + 1


def polygon(n: int, center: tuple[int, int], radius: int, offset: float = 0.0):
    if n < 1:
        return None
    elif n == 1:
        yield center
    else:
        da = 2 * pi / n

        def vert_x(angle):
            return int(sin(angle) * radius) + center[0]

        def vert_y(angle):
            return int(cos(angle) * radius) + center[1]

        prev = vert_x(offset), vert_y(offset)
        first = prev
        for vert in range(1, n):
            angle = offset + vert * da
            pos = vert_x(angle), vert_y(angle)
            yield from dda_line(prev, pos, 0)
            prev = pos
        yield from dda_line(pos, first)


def plot(
    func: Callable[[float], float],
    size: tuple[int, int],
    x_range: tuple[float, float],
    y_range: tuple[float, float],
):
    W, H = size
    left_W = -(W // 2)
    right_W = W + left_W

    dy = (y_range[1] - y_range[0]) / (H - 1)

    dx = (x_range[1] - x_range[0]) / (W - 1)
    xs = [x_range[0] + i * dx for i in range(W)]
    ys = [func(x) for x in xs]

    prev_pos = left_W, -round(ys[0] / dy)
    for y, i in zip(ys[1:-1], range(left_W + 1, right_W - 1)):
        pos = i, -round(y / dy)
        yield from dda_line(prev_pos, pos, end=0)
        prev_pos = pos
    last_pos = right_W, -round(ys[-1] / dy)
    yield from dda_line(prev_pos, last_pos, end=1)
