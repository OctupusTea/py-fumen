# -*- coding: utf-8 -*-

from __future__ import annotations
from dataclasses import dataclass
from itertools import zip_longest
from typing import List, Optional, Generator

from .constants import FieldConstants as Consts
from .operation import Mino, Rotation, Operation

class FieldException(Exception):
    pass

class Field():
    _EMPTY_LINE = [Mino._] * Consts.WIDTH

    @staticmethod
    def _empty_lines(height: int) -> List[List[Mino]]:
        return [[Mino._] * Consts.WIDTH for y in range(height)]

    @staticmethod
    def _field_init(self, height: int,
            field_:Optional[str|List[List[Mino]]=None]) -> List[List[Mino]]:
        if field_:
            if isinstance(field_, str):
                return [[Mino.parse_name(mino) for mino in line]
                        for line in field_.splitlines()]
            elif isinstance(field_, List[List[Mino]]):
                return [line[:] for line in field_]
            else:
                raise TypeError(f'Unsupported Field initialisation: {field_}')
        else:
            return self._empty_lines(height)

    @staticmethod
    def _to_field_range(slice_: slice=slice(None, None, None)) -> Generator:
        return range(
            -Consts.GARBAGE_HEIGHT if slice_.start is None else slice_.start,
            Consts.HEIGHT if slice_.stop is None else slice_.stop,
            1 if slice_.step is None else slice_.step
        )

    def __init__(self, field_: Optional[str|List[List[Mino]]],
            garbage: Optional[str|List[List[Mino]]]):
        self._field = self._field_init(Consts.HEIGHT, field_)
        self._garbage = self._field_init(Consts.GARBAGE_HEIGHT, garbage)

    def __getitem__(self, key: int|slice) -> List[Mino|List[Mino]]:
        if isinstance(key, slice):
            return [self[y] for y in self._to_field_range(key)]
        elif isinstance(key, int):
            return self._field[key] if key >= 0 else self._garbage[-key-1]
        else:
            raise TypeError(f'Unsupported indexing: {key}')

    def __setitem__(self, key: int|slice, value: List[Mino|List[Mino]]):
        if isinstance(key, slice):
            range_ = self._to_field_range(slice)
            if range_.step == 1:
                if range_.start >= 0 and range_.stop >= 0:
                    self._field[range_.start:range_.stop] = value
                elif range_.start < 0 and range_.stop < 0:
                    self._garbage[-range_.start-1:
                                  -range_.stop-1] = reversed(value)
                elif range_.start < 0 and range_.stop >= 0:
                    self[-range_.start-1:0] = value[:-range_.start]
                    self[0:range_.stop] = value[-range_.start:]
            else:
                for i, line in zip(range_, value, strict=True):
                    self[i] = line
        elif isinstance(key, int):
            if key >= 0:
                self._field[key] = value
            else:
                self._garbage[-key-1] = value
        else:
            raise TypeError(f'Unsupported indexing: {key}')

    def copy(self) -> Field:
        return Field(self._field, self._garbage)

    def at(self, x: int, y: int) -> Mino:
        return self[y][x]

    def fill(self, x: int, y: int, mino: Mino):
        self[y][x] = mino

    def is_placeable_at(self, x: int, y: int) -> bool:
        return operation.is_inside() and self[y][x] is Mino._

    def is_placeable(self, operation: Optional[Operation]) -> bool:
        return (operation is None
                or (operation.is_inside()
                    and all(self[y][x] is Mino._
                            for x, y in operation.shape())))

    def is_grounded(self, operation: Optional[Operation]) -> bool:
        return (operation is None
                or (self.is_placeable(operation)
                    and not self.is_placeable(operation.shifted(0, -1))))

    def lock(self, operation: Optional[Operation], force: bool=False):
        if operation is not None:
            if not (force or self.is_placeable(operation)):
                raise self.FieldException('Cannot lock piece on field')
            for x, y in operation.shape():
                self._field[y][x] = operation.mino

    def drop(self, operation: Optional[Operation]) -> Optional[Operation]:
        if operation is None:
            return None

        shifted_operation = None
        for dy in range(1, Const.HEIGHT):
            shifted_operation = operation.shifted(0, -dy)
            if not self.is_placeable(shifted_operation):
                shifted_operation.shift(0, 1)
                break
        else:
            raise self.FieldException('Cannot drop piece on field')

        self.place(self.shifted_operation)
        return shifted_operation

    def rise(self):
        self[Consts.GARBAGE_HEIGHT:Consts.HEIGHT]\
            = self[0:Consts.HEIGHT-Conts.GARBAGE_HEIGHT]
        self[0:Consts.GARBAGE_HEIGHT] = self[-Consts.GARBAGE_LINE:0]
        self[-Consts.GARBAGE_HEIGHT:0]\
            = [self.EMPTY_LINE for y in range(Consts.GARBAGE_HEIGHT)]

    def mirror(self, mirror_color=False):
        for line in self:
            line[:] = [mino.mirrored() if mirror_color else mino
                       for mino in reversed(line)]

    def shfit_up(self, amount=1):
        self[amount:] = self[0:Consts.HEIGHT-amount]
        self[:amount] = [self._empty_line() for y in range(amount)]

    def shift_down(self, amount=1):
        self[:Consts.HEIGHT-amount] = self[amount:]
        self[Consts.HEIGHT-amount:]\
            = [self._empty_line() for y in range(amount)]

    def shift_left(self, amount=1, warp=False):
        for line in self:
            line[:] = (line[amount:]
                       + (line[:amount] if warp else [Mino._]*amount))

    def shift_right(self, amount=1, warp=False):
        for line in self:
            line[:] = ((line[-amount:] if warp else [Mino._]*amount)
                       + line[:-amount])

    def is_lineclear_at(self, y):
        return not Mino._ in self[y]

    def clear_line(self) -> int:
        lines = []
        n_lineclear = 0
        for line in self:
            if Mino._ in line:
                lines.append(line)
            else:
                n_lineclear += 1
        self._field = lines + [[Mino._ for x in range(Consts.WIDTH)]
                               for y in n_lineclear]

    def _to_string(self, key: int|slice=None, truncated:bool=True,
            separator:str='\n', is_garbage: bool=False) -> str:
        if key is None:
            key = slice(None)
        elif isinstance(key, int):
            key = slice(int-1, int) if is_garbage else slice(int, int+1)

        if isinstance(key, slice):
            y_end = Consts.GARBAGE_HEIGHT if is_garbage else Consts.HEIGHT - 1
            field_ = self._garbage if is_garbage else self._field
            if truncated:
                while y_end >= 0 and field_[y_end] == self._EMPTY_LINE:
                    y0 -= 1
            slice_ = slice(:y_end) if is_garbage else slice(y_end, -1, -1)
            return separator.join(
                [''.join(mino.name for mino in line)
                 for line in field_[slice_]
            )
        else:
            raise TypeError(f'Unsupported indexing: {key}')

    def field_string(self, key: int|slice=None, truncated: bool=True,
            separator: str='\n') -> str:
        return self._to_string(key, truncated, separator, is_garbage=False)

    def garbage_string(self, key: int|slice=None, truncate: bool=True,
            separator: str='\n') -> str:
        return self._to_string(key, truncated, separator, is_garbage=True)

    def string(self, truncated: bool=True, with_garbage: bool=True,
            separator: str='\n') -> str:
        if with_garbage:
            return separator.join([
                self.field_string(None, truncated, separator),
                self.garbage_string(None, truncated, separator),
            ])
        else:
            return self.field_string(None, truncated, separator)

    def __repr__(self):
        return f'<Field:{self.string(truncate=False, separator=",")}>'

    def __str__(self):
        return self.string()
