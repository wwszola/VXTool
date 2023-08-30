from typing import Iterator, Generator, Callable, Iterable
from math import sqrt, pi, sin, cos
import random

from .core import Color, Rect, Dot, AnimatedDot

def animation(dot: Dot, **changes: dict[str, Iterable]):
    sorted = {}
    for name, frames in changes.items():
        for i, value in enumerate(frames):
            values = sorted.setdefault(i, dict()) 
            values[name] = value
    max_len = max(sorted.keys())
    for i in range(max_len + 1):
        yield dot.variant(**sorted[i])

def sign(x):
    if x > 1e-16: return 1
    elif x < 1e-16: return -1
    else: return 1
    
def snap(x):
    return sign(x) * (int(abs(x)))

def plot_func(func, size, x_range = (0, 1), y_range = (-1, 1), offset = (0, 0), snap: Callable = round):
    W, H = size
    left_W = - (W//2)
    right_W = W + left_W

    dy = (y_range[1] - y_range[0]) / (H - 1)

    dx = (x_range[1] - x_range[0]) / (W - 1)
    xs = [x_range[0] + i * dx for i in range(W)]
    ys = [func(x) for x in xs]
    
    prev_pos = left_W + offset[0], - snap(ys[0]/dy) + offset[1]
    for y, i in zip(ys[1:-1], range(left_W + 1, right_W - 1)):
        pos = i + offset[0], - snap(y/dy) + offset[1]
        yield from line_seq(prev_pos, pos, end = 0, snap = snap)
        prev_pos = pos
    last_pos = right_W + offset[0], -snap(ys[-1]/dy) + offset[1]
    yield from line_seq(prev_pos, last_pos, end = 1, snap = snap)

def plot_under_func(func, size, x_range = (0, 1), y_range = (-1, 1), offset = (0, 0), snap = round, y_end = 0):
    for X, Y in plot_func(func, size, x_range, y_range, offset, snap):
        yield from line_seq((X, Y), (X, y_end))

def words_line(text: str, pos: tuple[int, int] = (0, 0)) -> Generator:
    y = pos[1]
    for i, letter in enumerate(text):
        x = pos[0] + i
        yield (x, y), letter

def words_bound(text: str, region: Rect) -> Generator:
    pos = (0, 0)
    while len(text) > 0 and pos[1] < region.height:
        cut = region.width - pos[0]
        word = text[:cut]
        text = text[cut:]
        yield from words_line(
            word, 
            (pos[0] + region.left, pos[1] + region.top)
        )
        if pos[0] + len(word) >= region.width:
            pos = (0, pos[1] + 1)
        else:
            pos = (pos[0] + len(word), pos[1])

def scroll(text: str, window: int, start: int = 0) -> Iterator[str]:
    """yields views starting from empty view, shifts to left
    returns number of views yield

    Parameters:
    text: str
    window: int
        length of the view
    start: int = 0
        pass value < window to start from partially filled view
    """
    text = ' ' * window + text
    length = 0
    for pos in range(start, len(text) - window + 1):
        yield text[pos: pos + window]
        length += 1
    return length

def reveal(text: str, start: int = 0) -> Iterator[str]:
    d = len(text)
    for pos in range(start, d + 1):
        # yield text[0: pos] + ' ' * (d - pos)
        yield text[0: pos]
    return d

def line_seq(p1: tuple[float, float], p2: tuple[float, float], end: int = 1, snap: Callable = round) -> Generator:
    """DDA line generating algorithm"""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    step = max(abs(dx), abs(dy))
    
    if step <= 1e-16:
        yield snap(p1[0]), snap(p1[1])
    else:
        dx, dy = dx / step, dy / step
        for i in range(round(step) + end):
            x = p1[0] + i * dx
            y = p1[1] + i * dy
            yield snap(x), snap(y)

def grid_seq(shape: tuple[int, int], origin: tuple[int, int] = (0, 0)) -> Generator:
    for y in range(origin[1], origin[1] + shape[1]):
        for x in range(origin[0], origin[0] + shape[0]):
            yield (x, y)

def circle_seq(center: tuple[int, int], radius: int) -> Generator:
    def ends(half_chord: float):
        x_left = round(center[0] - half_chord)
        x_right = round(center[0] + half_chord)
        return x_left, x_right

    center = round(center[0]), round(center[1])
    radius = radius
    r_sq = radius ** 2
    caps_r = 0
    for d in range(1, radius):
        half_chord = sqrt(r_sq - d**2)
        x_left, x_right = ends(half_chord)
        for y in (center[1] - d, center[1] + d):
            yield from line_seq((x_left, y), (x_right, y))
        
        if x_right - x_left == 2 * radius:
            caps_r += 1

    x_left, x_right = ends(caps_r)
    for y in (center[1] - radius, center[1] + radius):
        yield from line_seq((x_left, y), (x_right, y))

    x_left, x_right = ends(radius)
    y = center[1]
    yield from line_seq((x_left, y), (x_right, y))

def polygon_seq(n: int, center: tuple[int, int], radius: int, offset: float = 0.0) -> Generator:
    if n < 1:
        return None
    elif n == 1:
        yield center
    else:
        da = 2 * pi / n
        vert_x = lambda angle: int(sin(angle) * radius) + center[0]
        vert_y = lambda angle: int(cos(angle) * radius) + center[1]
        prev = vert_x(offset), vert_y(offset)
        first = prev
        for vert in range(1, n):
            angle = offset + vert * da
            pos = vert_x(angle), vert_y(angle)
            yield from line_seq(prev, pos, 0)
            prev = pos
        yield from line_seq(pos, first)

def random_walk_x(dot: AnimatedDot, delta_time: int = 0, length: int = 1):
    for i in range(length):
        x = random.choice([-1,-1,0,1,1])
        dot.op_move(delta_time + i, (x, 0))
    return dot

def fade_in_fade_out(dot: AnimatedDot, delta_time: int = 0, length: int = 1, colors: list[Color] = []):
    dot.op_set(delta_time, 'color', colors)
    dot.op_set(delta_time + length - len(colors), 'color', colors[::-1])
    return dot

def spell_and_stop(dot: AnimatedDot, delta_time: int = 0, text: str = ''):
    dot.op_set(delta_time, 'letter', text)
    dot.op_stop(delta_time + len(text))
    return dot