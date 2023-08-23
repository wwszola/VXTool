from dataclasses import dataclass, field
from typing import Iterator, Generator
from copy import copy

from pygame import Color as PyGameColor
from pygame import Rect
from pygame.font import Font

class Color(PyGameColor):
    def __hash__(self):
        return hash(tuple(self))

    def __getstate__(self):
        return tuple(self)
    
    def __setstate__(self, rgba):
        self.update(rgba)

BLACK = Color(0, 0, 0, 255)

class Dot:
    def __init__(self, pos: tuple[int, int] = None, letter: str = None,
            color: Color = None, backcolor: Color = None, 
            font_family: str | None = None, font_size: int = None,
            clear: bool = True,
            ):
        self.pos: tuple[int, int] = pos
        self.letter: str = letter
        self.color: Color = color
        self.backcolor: Color = backcolor
        self.font_family: str = font_family
        self.font_size: str = font_size
        self.clear: str = clear

    def __str__(self) -> str:
        attrs = []
        for attr, value in self.__dict__.items():
            if value is not None:
                attrs.append(f"{attr}={value}")
        return "Dot(" + ", ".join(attrs) + ")"

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        # excluding self.pos
        return hash((
            self.letter, self.color, self.backcolor,
            self.font_family, self.font_size, self.clear
        ))

    def variant(self, **kwargs):
        new_dot = Dot.__new__(Dot)
        attr_names = ['pos', 'letter', 'color', 'backcolor', 'font_family', 'font_size', 'clear']
        for name in attr_names:
            if name in kwargs:
                setattr(new_dot, name, kwargs[name])
            else:
                setattr(new_dot, name, getattr(self, name))
        return new_dot

@dataclass
class Buffer():
    _container: dict[tuple[int, int], list[Dot]] = field(default_factory = dict)
    
    def is_empty(self):
        return all(len(local) == 0 for local in self._container.values())

    def put(self, dot: Dot):
        local: list[Dot] = self._container.setdefault(dot.pos, [])
        if dot.clear or dot.backcolor is not None:
            local.clear()
        local.append(dot)

    def diff(self, other):
        diff: Buffer = Buffer()
        clear_mask = set(self._container.keys()) - (other._container.keys())
        for pos in other._container.keys():
            if pos not in self._container:
                clear_mask.add(pos)
                diff._container[pos] = other._container[pos]
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

    def extend(self, dots: Iterator[Dot]):
        for dot in dots:
            self.put(dot)

    def erase(self, dot: Dot):
        try:
            local = self._container[dot.pos]
            local.remove(dot)
            if len(local) == 0:
                del self._container[dot.pos]
        except (KeyError, ValueError):
            pass
    
    def erase_at(self, pos: tuple[int, int], idx: int = -1):
        try:
            local = self._container[pos]
            local.pop(idx)
            if len(local) == 0:
                del self._container[pos]
        except (KeyError, IndexError):
            pass

    def clear(self):
        self._container.clear()

    def clear_at(self, pos):
        try:
            del self._container[pos]
        except KeyError:
            pass

    def merge(self, other):
        for dots in other._container.values():
            self.extend(dots)
        # self.extend(chain(other._container.values()))

    def edit_inp(self, pos: tuple[int, int], idx: int = -1, **kwargs):
        try:
            local = self._container[pos]
            old_dot = local.pop(idx)
            if 'pos' in list(kwargs.keys()):
                del kwargs[pos]
            new_dot = old_dot.variant(**kwargs)
            local.insert(idx, new_dot)
        except (KeyError, IndexError):
            pass
    
    def dot_seq(self) -> Generator:
        for pos, dots in self._container.items():
            yield from dots

    @staticmethod
    def from_dot_seq(dots):
        buffer = Buffer()
        buffer.extend(dots)
        return buffer

    def mask(self):
        yield from (key for key, value in self._container.items() if value)

    def cut(self, mask: Iterator[tuple[int, int]]):
        for pos in mask:
            self._container[pos] = []

    def translated(self, vec):
        sibling = Buffer()
        for dot in self.dot_seq():
            pos = dot.pos
            new_pos = pos[0] + vec[0], pos[1] + vec[1]
            sibling.put(dot.variant(pos = new_pos))
        return sibling

@dataclass
class BoundBuffer(Buffer):
    region: Rect = field(kw_only = True)

    def put(self, dot: Dot):
        if self.region.collidepoint(dot.pos):
            super().put(dot)