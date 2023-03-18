from dataclasses import dataclass, field
from typing import Iterator, Generator
from dataclasses import dataclass
from copy import copy

from pygame import Color as PyGameColor
from pygame import Rect
from pygame.font import Font

class Color(PyGameColor):
    def __hash__(self):
        return hash(tuple(self))

BLACK = Color(0, 0, 0, 255)

@dataclass(eq = True, frozen = True)
class Dot():
    pos: tuple[int, int] = field(default = None, hash = False, compare = False)
    
    letter: str = None
    color: Color = None
    backcolor: Color = field(default = None, kw_only = True)
    font: Font | None = None
    clear: bool = True

    @property
    def size(self):
        return self.font.size(self.letter)

    @property
    def rect(self) -> Rect:
        return Rect((0, 0), self.size)

    def variant(self, **kwargs):
        attrs = copy(self.__dict__)
        attrs.update(kwargs)
        return Dot(**attrs)


@dataclass
class Buffer():
    _container: dict[tuple[int, int], list[Dot]] = field(default_factory = dict)
    
    def put(self, dot: Dot):
        local: list[Dot] = self._container.setdefault(dot.pos, [])
        if dot.clear or dot.backcolor is not None:
            local.append(dot)
        else:
            try:
                local.remove(dot)
            except ValueError:
                pass
            finally:
               local.append(dot)

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
        yield from self._container.keys()

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