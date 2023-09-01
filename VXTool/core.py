from dataclasses import dataclass, field
from typing import Iterator, Generator, NamedTuple, Iterable
from copy import copy
from enum import Enum, auto

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
            clear: bool = True, align: str = 'center'
            ):
        self.pos: tuple[int, int] = pos
        self.letter: str = letter
        self.color: Color = color
        self.backcolor: Color = backcolor
        self.font_family: str = font_family
        self.font_size: str = font_size
        self.clear: str = clear
        self.align: str = align

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
            self.font_family, self.font_size, self.clear,
            self.align
        ))

    def variant(self, variant_class = None, **kwargs):
        if variant_class is None:
            variant_class = self.__class__
        new_dot = variant_class()
        for name, value in self.__dict__.items():
            if not hasattr(new_dot, name):
                continue
            if name in kwargs:
                setattr(new_dot, name, kwargs[name])
            else:
                setattr(new_dot, name, value)
        return new_dot

class Buffer():
    def __init__(self, dot_seq: Iterator[Dot] = []):
        self._container: dict[tuple[int, int], list[Dot]] = dict()
        if dot_seq:
            self.extend(dot_seq)

    def is_empty(self):
        return all(len(local) == 0 for local in self._container.values())

    def put(self, dot: Dot):
        local: list[Dot] = self._container.setdefault(dot.pos, [])
        if dot.clear or dot.backcolor is not None:
            local.clear()
        local.append(dot)

    def get_at(self, pos: tuple[int, int], idx: int = -1):
        try:
            local = self._container[pos]
            return local[idx]
        except (KeyError, ValueError):
            return None

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

    def mask(self):
        yield from (key for key, value in self._container.items() if value)

    def cut(self, mask: Iterator[tuple[int, int]]):
        for pos in mask:
            if pos in self._container: del self._container[pos]

class ANIMATION_OP(Enum):
    SET = auto()
    STOP = auto()
    JMP = auto()
    MOVE = auto()

class AnimationOp(NamedTuple):
    counter: int
    op_type: ANIMATION_OP
    args: list

    def __str__(self):
        return f"{self.counter}: {self.op_type.name} {self.args}"

class AnimatedDot(Dot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instructions: list[AnimationOp] = []
        self.frame_counter = 0
        self.instruction_pointer = 0
        self.new_pos: tuple[int, int] = None

    def _add_op(self, new_op: AnimationOp):
        idx = 0
        for op in self.instructions:
            if new_op.counter >= op.counter:
                idx += 1
            else:
                break
        self.instructions.insert(idx, new_op)

    def op_set(self, delta_time: int, attr_name: str, value):
        if hasattr(self, attr_name):
            if isinstance(value, Iterable):
                for i, x in enumerate(value):
                    self._add_op(AnimationOp(self.frame_counter + delta_time + i, ANIMATION_OP.SET, (attr_name, x)))
            else:
                self._add_op(AnimationOp(self.frame_counter + delta_time, ANIMATION_OP.SET, (attr_name, value)))

    def op_stop(self, delta_time):
        self._add_op(AnimationOp(self.frame_counter + delta_time, ANIMATION_OP.STOP, None))

    def op_jmp(self, delta_time: int, dst_delta_time: int):
        op_time = self.frame_counter + delta_time
        dst_time = self.frame_counter + dst_delta_time
        if dst_time < 0:
            dst_time = 0
        self._add_op(AnimationOp(op_time, ANIMATION_OP.JMP, (dst_time,)))

    def op_move(self, delta_time: int, move_vector: tuple[int, int], repeat: int = 1):
        op_time = self.frame_counter + delta_time
        for i in range(repeat):
            self._add_op(AnimationOp(op_time + i, ANIMATION_OP.MOVE, (move_vector,)))

    def _find_instruction_pointer(self, frame_counter):
        for i, op in enumerate(self.instructions):
            if op.counter <= frame_counter:
                return i

    def advance(self):
        result = True
        while result:
            if self.instruction_pointer >= len(self.instructions):
                break
            op = self.instructions[self.instruction_pointer]
            if self.frame_counter < op.counter: # does nothing when no instructions for now
                break
            match op.op_type:
                case ANIMATION_OP.STOP:
                    result = False
                case ANIMATION_OP.SET:
                    setattr(self, op.args[0], op.args[1])
                case ANIMATION_OP.JMP:
                    self.frame_counter = op.args[0]
                    self.instruction_pointer = self._find_instruction_pointer(op.args[0]) - 1
                case ANIMATION_OP.MOVE:
                    self.new_pos = self.pos[0] + op.args[0][0], self.pos[1] + op.args[0][1]
            self.instruction_pointer += 1
        self.frame_counter += 1
        return result
    
class AnimatedBuffer(Buffer):
    def __init__(self):
        super().__init__()
        self.animated_dots: list[AnimatedDot] = []
        self.counter = 0

    def put(self, dot: Dot):
        super().put(dot)
        if isinstance(dot, AnimatedDot):
            self.animated_dots.append(dot)

    def advance(self):
        dead_dots_idx = []
        for i, dot in enumerate(self.animated_dots):
            result = dot.advance()
            if not result:
                dead_dots_idx.append((i, dot))
                continue
            if dot.new_pos:
                super().erase(dot)
                dot.pos = dot.new_pos
                dot.new_pos = None
                super().put(dot)
        for i, (idx, dot) in enumerate(dead_dots_idx):
            self.animated_dots.pop(idx - i) # removing elements starts from the left, dead_dots_idx is sorted
            self.erase(dot)
        self.counter += 1