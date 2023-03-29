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
    @staticmethod
    def _to_field_range(slice_: slice=slice(None, None, None)) -> Generator:
        return range(
            -Consts.GARBAGE_HEIGHT if slice_.start is None else slice_.start,
            Consts.HEIGHT if slice_.stop is None else slice_.stop,
            1 if slice_.step is None else slice_.step
        )

    @staticmethod
    def _empty_line() -> List[Mino]:
        return [Mino._] * Consts.WIDTH

    def __init__(self):
        self._field = [[Mino._ for x in range(Consts.WIDTH)]
                       for y in range(Consts.HEIGHT)]
        self._garbage = [[Mino._ for x in range(Consts.WIDTH)]
                         for y in range(Consts.GARBAGE_HEIGHT)]

    def __getitem__(self, key: int|slice) -> List[Mino|List[Mino]]:
        if isinstance(key, slice):
            return [self[y] for y in self._to_field_range(key)]
        elif isinstance(key, int):
            return self._field[key] if key >= 0 else self._garbage[-key-1]
        else:
            raise KeyError(f'Unsupported indexing: {key}')

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
            raise KeyError(f'Unsupported indexing: {key}')

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
            = [self._empty_line() for y in range(Consts.GARBAGE_HEIGHT)]

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

    def string(self, truncate: bool=True, garbage: bool=True,
            separator: str='\n') -> str:
        y0 = Consts.HEIGHT - 1
        y_floor = -Consts.GARBAGE_HEIGHT if garbage else 0
        if truncate:
            while y0 >= y_floor and all(mino is Mino._ for mino in self[y0]):
                y0 -= 1

        return separator.join(
            [''.join(mino.name for mino in line)
                     for line in self[y0:y_floor-1:-1]]
        )

    def __repr__(self):
        return f'<Field:{self.string(truncate=False, separator=",")}>'

    def __str__(self):
        return self.string()
